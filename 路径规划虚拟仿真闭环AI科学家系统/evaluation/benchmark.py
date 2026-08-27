# evaluation/benchmark.py — 批量实验对比运行器

import json
from algorithms.astar import AStar
from algorithms.aco import AntColony
from algorithms.pso import ParticleSwarm
from algorithms.sa import SimulatedAnnealing
from algorithms.hybrid import HybridAlgorithm
from evaluation.metrics import evaluate_algorithm


# 算法工厂注册表：callable(seed, time_budget_s) -> 算法实例。
# 每次运行新建实例，算法内部 RNG 由 per-run 种子控制。
ALGORITHM_FACTORIES = {
    "A*": lambda seed, time_budget_s: AStar(time_budget_s=time_budget_s),
    "ACO": lambda seed, time_budget_s: AntColony(seed=seed, time_budget_s=time_budget_s),
    "PSO": lambda seed, time_budget_s: ParticleSwarm(seed=seed, time_budget_s=time_budget_s),
    "SA": lambda seed, time_budget_s: SimulatedAnnealing(seed=seed, time_budget_s=time_budget_s),
    "混合优化算法": lambda seed, time_budget_s: HybridAlgorithm(time_budget_s=time_budget_s),
}

# 兼容旧引用：按导入期默认参数暴露 bound search（不建议新代码使用）
ALGORITHMS = {
    name: factory(seed=None, time_budget_s=None).search
    for name, factory in ALGORITHM_FACTORIES.items()
}


class BenchmarkRunner:
    """在同一地图上批量运行5种算法并对比"""

    ALGORITHMS = ALGORITHM_FACTORIES

    def run(
        self,
        grid,
        start: tuple,
        target: tuple,
        n_runs: int = 5,
        compute_limit: str = "medium",
        base_seed: int = 0,
        time_budget_s: float = None,
    ) -> list:
        results = []
        for algo_index, (name, factory) in enumerate(ALGORITHM_FACTORIES.items()):
            metrics = evaluate_algorithm(
                factory,
                grid,
                start,
                target,
                n_runs,
                compute_limit=compute_limit,
                base_seed=base_seed,
                algo_index=algo_index,
                time_budget_s=time_budget_s,
                algorithm_name=name,
            )
            metrics["algorithm"] = name
            results.append(metrics)

        results.sort(key=lambda r: r["success_rate"], reverse=True)
        return results

    def run_dynamic_sequence(
        self,
        grids: list,
        start: tuple,
        target: tuple,
        n_runs: int = 3,
        compute_limit: str = "medium",
        base_seed: int = 0,
        time_budget_s: float = None,
    ) -> list:
        """在动态地图序列的每个时间片上重规划，并汇总五算法表现。"""
        if not grids:
            return []

        results = []
        for algo_index, (name, factory) in enumerate(ALGORITHM_FACTORIES.items()):
            frame_metrics = []
            for frame_idx, grid in enumerate(grids):
                # 每帧种子空间偏移 1000，与算法/重复维度（*100/+run）不冲突
                metrics = evaluate_algorithm(
                    factory,
                    grid,
                    start,
                    target,
                    n_runs,
                    compute_limit=compute_limit,
                    base_seed=base_seed + frame_idx * 1000,
                    algo_index=algo_index,
                    time_budget_s=time_budget_s,
                    algorithm_name=name,
                )
                frame_metrics.append(metrics)

            summary = self._summarize_dynamic_metrics(frame_metrics)
            summary["algorithm"] = name
            summary["dynamic_steps"] = len(frame_metrics)
            results.append(summary)

        results.sort(key=lambda r: r["success_rate"], reverse=True)
        return results

    @staticmethod
    def _summarize_dynamic_metrics(frame_metrics: list) -> dict:
        if not frame_metrics:
            return {
                "avg_time": 0.0,
                "avg_path_length": 0.0,
                "success_rate": 0.0,
                "reported_success_rate": 0.0,
                "timeout_rate": 0.0,
                "stability_score": 0.0,
                "smoothness": 0.0,
                "safety_score": 0.0,
                "expanded_nodes": 0,
                "turning_points": 0,
                "compute_cost": 0.0,
                "robustness": 0.0,
                "dynamic_failure_frames": 0,
                "runs": [],
            }

        def _mean(key: str) -> float:
            values = [float(m.get(key, 0.0) or 0.0) for m in frame_metrics]
            return sum(values) / max(len(values), 1)

        failure_frames = sum(
            1 for m in frame_metrics if float(m.get("success_rate", 0.0) or 0.0) < 0.5
        )
        all_runs = [run for m in frame_metrics for run in m.get("runs", [])]
        return {
            "avg_time": round(_mean("avg_time"), 4),
            "avg_path_length": round(_mean("avg_path_length"), 1),
            "success_rate": round(_mean("success_rate"), 2),
            "reported_success_rate": round(_mean("reported_success_rate"), 2),
            "timeout_rate": round(_mean("timeout_rate"), 2),
            "stability_score": round(_mean("stability_score"), 4),
            "smoothness": round(_mean("smoothness"), 4),
            "safety_score": round(_mean("safety_score"), 4),
            "expanded_nodes": int(round(_mean("expanded_nodes"))),
            "turning_points": int(round(_mean("turning_points"))),
            "compute_cost": round(_mean("compute_cost"), 4),
            "robustness": round(_mean("robustness"), 4),
            "dynamic_failure_frames": failure_frames,
            "runs": all_runs,
        }

    def save(self, results: list, filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    def print_table(self, results: list):
        print(f"\n{'算法':<10} {'平均耗时(s)':<12} {'路径长度':<10} {'成功率':<8} {'稳定性':<8}")
        print("-" * 55)
        for r in results:
            print(f"{r['algorithm']:<10} {r['avg_time']:<12.4f} {r['avg_path_length']:<10} "
                  f"{r['success_rate']:<8.2f} {r['stability_score']:<8.4f}")
