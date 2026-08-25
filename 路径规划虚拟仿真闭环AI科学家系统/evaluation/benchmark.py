# evaluation/benchmark.py — 批量实验对比运行器

import json
from algorithms.astar import AStar
from algorithms.aco import AntColony
from algorithms.pso import ParticleSwarm
from algorithms.sa import SimulatedAnnealing
from algorithms.hybrid import HybridAlgorithm
from evaluation.metrics import evaluate_algorithm


class BenchmarkRunner:
    """在同一地图上批量运行5种算法并对比"""

    ALGORITHMS = {
        "A*": AStar().search,
        "ACO": AntColony().search,
        "PSO": ParticleSwarm().search,
        "SA": SimulatedAnnealing().search,
        "混合优化算法": HybridAlgorithm().search,
    }

    def run(
        self,
        grid,
        start: tuple,
        target: tuple,
        n_runs: int = 5,
        compute_limit: str = "medium",
    ) -> list:
        results = []
        for name, algo_func in self.ALGORITHMS.items():
            metrics = evaluate_algorithm(
                algo_func,
                grid,
                start,
                target,
                n_runs,
                compute_limit=compute_limit,
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
    ) -> list:
        """在动态地图序列的每个时间片上重规划，并汇总五算法表现。"""
        if not grids:
            return []

        results = []
        for name, algo_func in self.ALGORITHMS.items():
            frame_metrics = []
            for grid in grids:
                metrics = evaluate_algorithm(
                    algo_func,
                    grid,
                    start,
                    target,
                    n_runs,
                    compute_limit=compute_limit,
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
                "stability_score": 0.0,
                "smoothness": 0.0,
                "safety_score": 0.0,
                "expanded_nodes": 0,
                "turning_points": 0,
                "compute_cost": 0.0,
                "robustness": 0.0,
                "dynamic_failure_frames": 0,
            }

        def _mean(key: str) -> float:
            values = [float(m.get(key, 0.0) or 0.0) for m in frame_metrics]
            return sum(values) / max(len(values), 1)

        failure_frames = sum(
            1 for m in frame_metrics if float(m.get("success_rate", 0.0) or 0.0) < 0.5
        )
        return {
            "avg_time": round(_mean("avg_time"), 4),
            "avg_path_length": round(_mean("avg_path_length"), 1),
            "success_rate": round(_mean("success_rate"), 2),
            "stability_score": round(_mean("stability_score"), 4),
            "smoothness": round(_mean("smoothness"), 4),
            "safety_score": round(_mean("safety_score"), 4),
            "expanded_nodes": int(round(_mean("expanded_nodes"))),
            "turning_points": int(round(_mean("turning_points"))),
            "compute_cost": round(_mean("compute_cost"), 4),
            "robustness": round(_mean("robustness"), 4),
            "dynamic_failure_frames": failure_frames,
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
