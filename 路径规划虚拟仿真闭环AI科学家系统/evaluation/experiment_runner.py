# evaluation/experiment_runner.py — 批量实验矩阵运行器

import json
import os
import time
from typing import Optional

import numpy as np

from algorithms.astar import AStar
from algorithms.aco import AntColony
from algorithms.pso import ParticleSwarm
from algorithms.sa import SimulatedAnnealing
from algorithms.hybrid import HybridAlgorithm
from config import EXPERIMENTS_DIR
from data.experiment_db import ExperimentDB
from evaluation.benchmark import BenchmarkRunner
from evaluation.metrics import evaluate_algorithm
from map.map_generator import MapGenerator


COMPLEXITY_LEVELS = [0.15, 0.35, 0.65]
SCALES = [(50, 50), (100, 100), (200, 200)]
COMPUTE_LIMITS = ["low", "medium", "high"]


def _make_fast_aco():
    aco = AntColony()
    aco.n_ants = 10
    aco.n_iterations = 20
    return aco.search


def _make_fast_pso():
    return ParticleSwarm(n_particles=10, n_iterations=20).search


def _make_fast_sa():
    sa = SimulatedAnnealing()
    sa.initial_temp = 100.0
    sa.cooling_rate = 0.9
    sa.max_iter_per_temp = 10
    return sa.search


ALGORITHM_REGISTRY = {
    "A*": lambda: AStar().search,
    "ACO": _make_fast_aco,
    "PSO": _make_fast_pso,
    "SA": _make_fast_sa,
    "混合优化算法": lambda: HybridAlgorithm().search,
}


def _complexity_label(obstacle_ratio: float) -> str:
    if obstacle_ratio < 0.20:
        return "低复杂度"
    if obstacle_ratio <= 0.50:
        return "中复杂度"
    return "高复杂度"


class ExperimentRunner:
    """3×3×3 实验矩阵运行器：复杂度 × 规模 × 算力"""

    def __init__(self, db: Optional[ExperimentDB] = None):
        self.db = db or ExperimentDB()
        self.generator = MapGenerator()

    def _build_grid(self, width: int, height: int, obstacle_ratio: float, seed: int):
        gen = MapGenerator(seed=seed)
        start = (0, 0)
        target = (width - 1, height - 1)
        return gen.generate(width, height, obstacle_ratio, start, target), start, target

    def _evaluate_one(
        self,
        obstacle_ratio: float,
        scale: tuple,
        compute_limit: str,
        n_maps: int,
        n_runs_per_algo: int,
        base_seed: int = 0,
        dynamic_change_rate: float = 0.0,
        dynamic_steps: int = 5,
    ) -> list:
        width, height = scale
        results = []
        for map_idx in range(n_maps):
            seed = base_seed + map_idx + int(obstacle_ratio * 1000) + width
            if dynamic_change_rate > 0:
                gen = MapGenerator(seed=seed)
                start = (0, 0)
                target = (width - 1, height - 1)
                grids = gen.generate_dynamic_sequence(
                    width=width,
                    height=height,
                    obstacle_ratio=obstacle_ratio,
                    dynamic_change_rate=dynamic_change_rate,
                    steps=dynamic_steps,
                    start=start,
                    target=target,
                )
                grid = grids[0]
            else:
                grid, start, target = self._build_grid(width, height, obstacle_ratio, seed)
                grids = [grid]

            map_id = self.db.insert_map(
                source="experiment_runner",
                map_type="dynamic_random" if dynamic_change_rate > 0 else "random",
                width=width,
                height=height,
                obstacle_ratio=obstacle_ratio,
                connectivity=0.5,
                topology_randomness=0.5,
                dynamic_change_rate=dynamic_change_rate,
            )

            for algo_name, algo_factory in ALGORITHM_REGISTRY.items():
                algo_func = algo_factory()
                try:
                    if dynamic_change_rate > 0:
                        frame_metrics = [
                            evaluate_algorithm(
                                algo_func, frame, start, target,
                                n_runs=n_runs_per_algo, compute_limit=compute_limit,
                            )
                            for frame in grids
                        ]
                        metrics = BenchmarkRunner._summarize_dynamic_metrics(frame_metrics)
                        metrics["dynamic_steps"] = len(grids)
                    else:
                        metrics = evaluate_algorithm(
                            algo_func, grid, start, target,
                            n_runs=n_runs_per_algo, compute_limit=compute_limit,
                        )
                except Exception as exc:
                    metrics = {
                        "avg_time": 0.0, "avg_path_length": 0.0, "success_rate": 0.0,
                        "stability_score": 0.0, "smoothness": 0.0, "safety_score": 0.0,
                        "expanded_nodes": 0, "turning_points": 0, "compute_cost": 0.0,
                        "robustness": 0.0,
                    }
                    print(f"[!] {algo_name} on map {map_idx} failed: {exc}")

                self.db.insert_run(
                    map_id=map_id,
                    algorithm=algo_name,
                    runtime=metrics["avg_time"],
                    path_length=metrics["avg_path_length"],
                    success=bool(metrics["success_rate"] >= 0.5),
                    expanded_nodes=metrics["expanded_nodes"],
                    turning_points=metrics["turning_points"],
                    smoothness=metrics["smoothness"],
                    safety_score=metrics["safety_score"],
                    stability_score=metrics["stability_score"],
                    compute_cost=metrics.get("compute_cost", 0.0),
                    robustness=metrics.get("robustness", 0.0),
                    parameters={
                        "scale": [width, height],
                        "obstacle_ratio": obstacle_ratio,
                        "compute_limit": compute_limit,
                        "dynamic_change_rate": dynamic_change_rate,
                        "dynamic_steps": len(grids),
                    },
                    compute_limit=compute_limit,
                    seed=seed,
                )

                results.append({
                    "map_idx": map_idx,
                    "obstacle_ratio": obstacle_ratio,
                    "scale": [width, height],
                    "compute_limit": compute_limit,
                    "dynamic_change_rate": dynamic_change_rate,
                    "dynamic_steps": len(grids),
                    "algorithm": algo_name,
                    **metrics,
                })
        return results

    def run_matrix(
        self,
        n_maps_per_config: int = 10,
        n_runs_per_algo: int = 3,
        complexities: list = None,
        scales: list = None,
        compute_limits: list = None,
        dynamic_change_rates: list = None,
        dynamic_steps: int = 5,
    ) -> list:
        """实验矩阵：复杂度 × 规模 × 算力 × 动态变化率"""
        complexities = complexities or COMPLEXITY_LEVELS
        scales = scales or SCALES
        compute_limits = compute_limits or COMPUTE_LIMITS
        dynamic_change_rates = dynamic_change_rates or [0.0]

        all_results = []
        total_configs = len(complexities) * len(scales) * len(compute_limits) * len(dynamic_change_rates)
        config_idx = 0
        t0 = time.perf_counter()
        for obs in complexities:
            for scale in scales:
                for compute_limit in compute_limits:
                    for dynamic_change_rate in dynamic_change_rates:
                        config_idx += 1
                        label = _complexity_label(obs)
                        print(
                            f"[{config_idx}/{total_configs}] "
                            f"obstacle={obs:.2f} ({label}) scale={scale} "
                            f"compute={compute_limit} dynamic={dynamic_change_rate:.2f}"
                        )
                        results = self._evaluate_one(
                            obs, scale, compute_limit, n_maps_per_config, n_runs_per_algo,
                            base_seed=config_idx * 1000,
                            dynamic_change_rate=float(dynamic_change_rate or 0.0),
                            dynamic_steps=dynamic_steps,
                        )
                        all_results.extend(results)
        elapsed = time.perf_counter() - t0
        print(f"\n[DONE] 矩阵实验完成：{len(all_results)} 条记录，耗时 {elapsed:.1f} 秒")
        return all_results

    def run_quick(
        self,
        n_maps_per_complexity: int = 10,
        scale: tuple = (50, 50),
        compute_limit: str = "medium",
        n_runs_per_algo: int = 3,
        dynamic_change_rate: float = 0.0,
        dynamic_steps: int = 5,
    ) -> list:
        """快速模式：3 复杂度 × N 地图 × 5 算法（单规模 + 单算力）"""
        results = []
        t0 = time.perf_counter()
        for obs in COMPLEXITY_LEVELS:
            label = _complexity_label(obs)
            print(
                f"[quick] obstacle={obs:.2f} ({label}) scale={scale} "
                f"compute={compute_limit} dynamic={dynamic_change_rate:.2f}"
            )
            results.extend(
                self._evaluate_one(
                    obs, scale, compute_limit, n_maps_per_complexity, n_runs_per_algo,
                    dynamic_change_rate=dynamic_change_rate,
                    dynamic_steps=dynamic_steps,
                )
            )
        elapsed = time.perf_counter() - t0
        print(f"\n[DONE] 快速实验完成：{len(results)} 条记录，耗时 {elapsed:.1f} 秒")
        return results

    def generate_summary_xlsx(self, filepath: Optional[str] = None) -> str:
        """导出汇总 xlsx：按 (algorithm, scale, compute_limit, obstacle_ratio) 聚合"""
        from openpyxl import Workbook

        if filepath is None:
            os.makedirs(EXPERIMENTS_DIR, exist_ok=True)
            filepath = os.path.join(EXPERIMENTS_DIR, "benchmark_summary.xlsx")

        cur = self.db.conn.execute(
            """
            SELECT m.obstacle_ratio AS obstacle_ratio,
                   m.width AS width,
                   m.height AS height,
                   r.algorithm AS algorithm,
                   r.compute_limit AS compute_limit,
                   COUNT(*) AS n_runs,
                   AVG(r.runtime) AS avg_runtime,
                   AVG(r.path_length) AS avg_path_length,
                   AVG(r.success) AS avg_success_rate,
                   AVG(r.smoothness) AS avg_smoothness,
                   AVG(r.safety_score) AS avg_safety,
                   AVG(r.stability_score) AS avg_stability,
                   AVG(r.expanded_nodes) AS avg_expanded,
                   AVG(r.compute_cost) AS avg_compute_cost,
                   AVG(r.turning_points) AS avg_turning_points,
                   AVG(r.robustness) AS avg_robustness
            FROM algorithm_runs r
            JOIN maps m ON r.map_id = m.map_id
            GROUP BY m.obstacle_ratio, m.width, m.height, r.algorithm, r.compute_limit
            ORDER BY m.obstacle_ratio, m.width, r.algorithm
            """
        )
        rows = cur.fetchall()
        col_names = [d[0] for d in cur.description]

        wb = Workbook()
        ws = wb.active
        ws.title = "benchmark_summary"
        ws.append(col_names)
        for row in rows:
            ws.append([row[c] for c in col_names])

        algo_ws = wb.create_sheet("by_algorithm")
        cur2 = self.db.conn.execute(
            """
            SELECT algorithm AS algorithm,
                   COUNT(*) AS n_runs,
                   AVG(runtime) AS avg_runtime,
                   AVG(path_length) AS avg_path_length,
                   AVG(success) AS avg_success_rate,
                   AVG(smoothness) AS avg_smoothness,
                   AVG(safety_score) AS avg_safety,
                   AVG(stability_score) AS avg_stability,
                   AVG(compute_cost) AS avg_compute_cost,
                   AVG(robustness) AS avg_robustness
            FROM algorithm_runs
            GROUP BY algorithm
            ORDER BY avg_success_rate DESC
            """
        )
        algo_cols = [d[0] for d in cur2.description]
        algo_ws.append(algo_cols)
        for row in cur2.fetchall():
            algo_ws.append([row[c] for c in algo_cols])

        wb.save(filepath)
        return filepath

    def generate_failure_cases(self, filepath: Optional[str] = None) -> str:
        """导出所有 success=0 的失败案例到 jsonl"""
        if filepath is None:
            os.makedirs(EXPERIMENTS_DIR, exist_ok=True)
            filepath = os.path.join(EXPERIMENTS_DIR, "failure_cases.jsonl")

        cur = self.db.conn.execute(
            """
            SELECT r.run_id, r.map_id, m.obstacle_ratio, m.width, m.height,
                   r.algorithm, r.compute_limit, r.runtime, r.path_length,
                   r.expanded_nodes, r.turning_points, r.smoothness,
                   r.safety_score, r.stability_score, r.compute_cost,
                   r.robustness, r.created_at
            FROM algorithm_runs r
            JOIN maps m ON r.map_id = m.map_id
            WHERE r.success = 0
            ORDER BY r.created_at
            """
        )
        rows = cur.fetchall()
        with open(filepath, "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(dict(row), ensure_ascii=False) + "\n")
        return filepath
