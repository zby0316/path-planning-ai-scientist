# agents/experiment_agent.py — 实验验证智能体（Phase 5，提示词 5-2）
"""根据 HypothesisAgent 的 experiment_plan 自动跑验证实验，对比各算法表现并判断假设是否成立。"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from agents.research_state import ResearchState
from data.experiment_db import ExperimentDB
from evaluation.benchmark import BenchmarkRunner
from map.map_generator import MapGenerator

logger = logging.getLogger(__name__)

__all__ = ["ExperimentAgent"]

_DEFAULT_ALGORITHMS = ["A*", "ACO", "PSO", "SA", "混合优化算法"]
_DEFAULT_METRICS = ["success_rate", "avg_time", "avg_path_length", "stability_score"]
_SUCCESS_RATE_GAP = 0.10  # 推荐算法需 > 次优算法 10% 才认为假设成立


def _scene_to_obstacle_ratio(scene_level: str) -> float:
    return {
        "低复杂度": 0.10,
        "中复杂度": 0.35,
        "高复杂度": 0.65,
    }.get(scene_level, 0.35)


class ExperimentAgent:
    """实验验证智能体（Phase 5，提示词 5-2）。"""

    def __init__(self, db: ExperimentDB, benchmark_runner: BenchmarkRunner) -> None:
        self.db = db
        self.benchmark_runner = benchmark_runner

    # ------------------------------------------------------------------ #
    def _default_experiment_plan(self, state: ResearchState) -> Dict[str, Any]:
        """默认实验方案：50 张地图、5 算法、5 重复。"""
        env = state.env_input or {}
        scene_level = (state.decision or {}).get("scene_level", "")
        obstacle_ratio = float(env.get("obstacle_ratio") or _scene_to_obstacle_ratio(scene_level))
        width = int(env.get("map_width") or 100)
        height = int(env.get("map_height") or 100)
        return {
            "maps": {
                "count": 50,
                "width": width,
                "height": height,
                "obstacle_ratio": obstacle_ratio,
                "dynamic_change_rate": float(env.get("dynamic_change_rate", 0.0) or 0.0),
                "dynamic_steps": 5,
            },
            "algorithms": list(_DEFAULT_ALGORITHMS),
            "runs_per_algorithm": 5,
            "metrics": list(_DEFAULT_METRICS),
        }

    # ------------------------------------------------------------------ #
    def run_validation(self, state: ResearchState) -> ResearchState:
        """根据 experiment_plan 自动跑实验，汇总后判定假设是否成立。"""
        if state.metadata is None:
            state.metadata = {}
        state.metadata.setdefault("errors", [])

        plan = (state.hypothesis or {}).get("experiment_plan") or self._default_experiment_plan(state)
        maps_cfg = plan.get("maps", {}) or {}
        n_maps = int(maps_cfg.get("count", 50))
        width = int(maps_cfg.get("width", 100))
        height = int(maps_cfg.get("height", 100))
        obstacle_ratio = float(maps_cfg.get("obstacle_ratio", 0.35))
        dynamic_change_rate = float(
            maps_cfg.get(
                "dynamic_change_rate",
                (state.env_input or {}).get("dynamic_change_rate", 0.0),
            )
            or 0.0
        )
        dynamic_steps = max(1, int(maps_cfg.get("dynamic_steps", 5)))
        n_runs = int(plan.get("runs_per_algorithm", 5))

        per_algo_metrics: Dict[str, Dict[str, Any]] = {}
        for algo in _DEFAULT_ALGORITHMS:
            per_algo_metrics[algo] = {
                "algorithm": algo,
                "n_maps": 0,
                "n_success": 0,
                "runtime_sum": 0.0,
                "path_length_sum": 0.0,
                "stability_sum": 0.0,
                "dynamic_failure_frames_sum": 0,
            }

        for map_idx in range(n_maps):
            seed = map_idx * 7 + int(obstacle_ratio * 1000) + width
            try:
                gen = MapGenerator(seed=seed)
                start = (0, 0)
                target = (width - 1, height - 1)
                if dynamic_change_rate > 0:
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
                    grid = gen.generate(width, height, obstacle_ratio, start, target)
                    grids = [grid]
            except Exception as exc:
                logger.error("ExperimentAgent 第 %s 张地图生成失败: %s", map_idx, exc, exc_info=True)
                state.metadata["errors"].append(
                    f"ExperimentAgent 第 {map_idx} 张地图生成失败: {exc}"
                )
                continue
            try:
                map_id = self.db.insert_map(
                    source="experiment_agent",
                    map_type="dynamic_random" if dynamic_change_rate > 0 else "random",
                    width=width,
                    height=height,
                    obstacle_ratio=obstacle_ratio,
                    connectivity=0.5,
                    topology_randomness=0.5,
                    dynamic_change_rate=dynamic_change_rate,
                )
            except Exception as exc:
                logger.error("ExperimentAgent insert_map 失败 (map_idx=%s): %s", map_idx, exc, exc_info=True)
                state.metadata["errors"].append(
                    f"ExperimentAgent insert_map 失败 (map_idx={map_idx}): {exc}"
                )
                continue
            try:
                if dynamic_change_rate > 0:
                    results = self.benchmark_runner.run_dynamic_sequence(
                        grids,
                        start,
                        target,
                        n_runs=n_runs,
                        compute_limit=(state.env_input or {}).get("compute_limit", "medium"),
                    )
                else:
                    results = self.benchmark_runner.run(
                        grid,
                        start,
                        target,
                        n_runs=n_runs,
                        compute_limit=(state.env_input or {}).get("compute_limit", "medium"),
                    )
            except Exception as exc:
                logger.error("ExperimentAgent BenchmarkRunner.run 失败 (map_idx=%s): %s", map_idx, exc, exc_info=True)
                state.metadata["errors"].append(
                    f"ExperimentAgent BenchmarkRunner.run 失败 (map_idx={map_idx}): {exc}"
                )
                continue
            for r in results:
                algo = r.get("algorithm", "unknown")
                if algo not in per_algo_metrics:
                    continue
                m = per_algo_metrics[algo]
                m["n_maps"] += 1
                avg_time = float(r.get("avg_time", 0.0) or 0.0)
                avg_path = float(r.get("avg_path_length", 0.0) or 0.0)
                succ = float(r.get("success_rate", 0.0) or 0.0)
                stab = float(r.get("stability_score", 0.0) or 0.0)
                m["runtime_sum"] += avg_time
                m["path_length_sum"] += avg_path
                m["stability_sum"] += stab
                m["dynamic_failure_frames_sum"] += int(r.get("dynamic_failure_frames", 0) or 0)
                if succ >= 0.5:
                    m["n_success"] += 1
                # 写 SQLite
                try:
                    self.db.insert_run(
                        map_id=map_id,
                        algorithm=algo,
                        runtime=avg_time,
                        path_length=avg_path,
                        success=bool(succ >= 0.5),
                        expanded_nodes=int(r.get("expanded_nodes", 0) or 0),
                        turning_points=int(r.get("turning_points", 0) or 0),
                        smoothness=float(r.get("smoothness", 0.0) or 0.0),
                        safety_score=float(r.get("safety_score", 0.0) or 0.0),
                        stability_score=stab,
                        compute_cost=float(r.get("compute_cost", 0.0) or 0.0),
                        robustness=float(r.get("robustness", 0.0) or 0.0),
                        parameters={
                            "obstacle_ratio": obstacle_ratio,
                            "width": width,
                            "height": height,
                            "n_runs": n_runs,
                            "dynamic_change_rate": dynamic_change_rate,
                            "dynamic_steps": len(grids),
                        },
                        compute_limit=(state.env_input or {}).get("compute_limit", "medium"),
                        seed=seed,
                    )
                except Exception as exc:
                    logger.error("ExperimentAgent insert_run 失败 (algo=%s, map_idx=%s): %s", algo, map_idx, exc, exc_info=True)
                    state.metadata["errors"].append(
                        f"ExperimentAgent insert_run 失败 (algo={algo}, map_idx={map_idx}): {exc}"
                    )

        # 汇总
        state.experiment_results = []
        for algo, m in per_algo_metrics.items():
            n = max(m["n_maps"], 1)
            state.experiment_results.append({
                "algorithm": algo,
                "n_maps": m["n_maps"],
                "success_rate": round(m["n_success"] / n, 4),
                "avg_runtime": round(m["runtime_sum"] / n, 4),
                "avg_path_length": round(m["path_length_sum"] / n, 2),
                "stability_score": round(m["stability_sum"] / n, 4),
                "dynamic_change_rate": round(dynamic_change_rate, 4),
                "dynamic_steps": dynamic_steps if dynamic_change_rate > 0 else 1,
                "dynamic_failure_frames": int(m["dynamic_failure_frames_sum"]),
            })
        # 排序：success_rate desc
        state.experiment_results.sort(key=lambda r: r["success_rate"], reverse=True)

        # 判定假设是否成立
        self.compare_with_hypothesis(state)
        return state

    # ------------------------------------------------------------------ #
    def compare_with_hypothesis(self, state: ResearchState) -> bool:
        """把实验结果与假设预期对比，返回 bool 同时写入 metadata。"""
        if state.metadata is None:
            state.metadata = {}
        expected_algo = (
            (state.hypothesis or {}).get("expected_results", {}).get("best_algorithm")
            or (state.decision or {}).get("best_algorithm")
            or ""
        )
        results = state.experiment_results or []
        if not expected_algo or len(results) < 2:
            state.metadata["hypothesis_supported"] = False
            state.metadata["hypothesis_support_score"] = 0.0
            return False

        # 找到 expected_algo 与次优的 success_rate
        my_rate = 0.0
        other_rates = []
        for r in results:
            algo = r.get("algorithm", "")
            sr = float(r.get("success_rate", 0) or 0)
            if algo == expected_algo:
                my_rate = sr
            else:
                other_rates.append((algo, sr))
        if not other_rates:
            state.metadata["hypothesis_supported"] = False
            state.metadata["hypothesis_support_score"] = 0.0
            return False
        # 次优 = other_rates 中最高
        second_best_algo, second_best_rate = max(other_rates, key=lambda x: x[1])
        gap = my_rate - second_best_rate
        supported = gap > _SUCCESS_RATE_GAP
        # 连续分：夹到 [0, 1]
        support_score = max(0.0, min(1.0, 0.5 + gap))
        state.metadata["hypothesis_supported"] = bool(supported)
        state.metadata["hypothesis_support_score"] = round(support_score, 4)
        state.metadata["hypothesis_support_details"] = {
            "expected_algorithm": expected_algo,
            "expected_success_rate": my_rate,
            "second_best_algorithm": second_best_algo,
            "second_best_success_rate": second_best_rate,
            "gap": round(gap, 4),
        }
        return bool(supported)
