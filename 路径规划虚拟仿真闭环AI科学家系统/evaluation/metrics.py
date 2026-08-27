# evaluation/metrics.py — 性能指标计算（10 维扩展版 + 逐次明细 + 独立校验）

import time

import numpy as np
from scipy.ndimage import distance_transform_edt

from config import RUNTIME_BUDGET_S
from evaluation.path_validator import (
    evaluate_run_result,
    validate_path,
)


def _count_turning_points(path) -> int:
    if not path or len(path) < 3:
        return 0
    turns = 0
    prev_dx, prev_dy = None, None
    for i in range(1, len(path)):
        x0, y0 = path[i - 1]
        x1, y1 = path[i]
        dx, dy = x1 - x0, y1 - y0
        if dx == 0 and dy == 0:
            continue
        norm = max(abs(dx), abs(dy))
        sx, sy = int(dx // norm if norm else 0), int(dy // norm if norm else 0)
        if prev_dx is not None and (sx, sy) != (prev_dx, prev_dy):
            turns += 1
        prev_dx, prev_dy = sx, sy
    return turns


def _smoothness(path_length: int, turning_points: int) -> float:
    if path_length <= 1:
        return 0.0
    return round(turning_points / (path_length - 1), 4)


def _safety_score(path, grid: np.ndarray) -> float:
    if not path or len(path) == 0:
        return 0.0
    h, w = grid.shape
    obstacles = (grid == 1)
    if not obstacles.any():
        return 1.0
    dist_map = distance_transform_edt(~obstacles)
    total = 0.0
    for x, y in path:
        if 0 <= x < w and 0 <= y < h:
            total += float(dist_map[y, x])
        else:
            total += 0.0
    avg_dist = total / len(path)
    norm = max(w, h)
    return round(min(max(avg_dist / norm, 0.0), 1.0), 4)


def _compute_cost(expanded_nodes: int) -> float:
    if expanded_nodes <= 0:
        return 0.0
    raw = expanded_nodes * np.log(expanded_nodes + 1) / 10000.0
    return round(min(max(raw, 0.0), 1.0), 4)


def _run_seed(base_seed: int, algo_index: int, run_idx: int) -> int:
    """确定性种子派生：每图 × 每算法 × 每次重复唯一且可复现。"""
    return int(base_seed) + int(algo_index) * 100 + int(run_idx)


def _robustness(
    algorithm_factory,
    grid: np.ndarray,
    start: tuple,
    target: tuple,
    algorithm_name: str = "",
    n_perturbations: int = 3,
    perturb_ratio: float = 0.05,
    seed: int = 0,
    time_budget_s: float = None,
) -> float:
    h, w = grid.shape
    rng = np.random.RandomState(seed)
    free_indices = np.argwhere(grid == 0)
    if len(free_indices) == 0:
        return 0.0

    successes = 0
    perturb_count = max(1, int(len(free_indices) * perturb_ratio))
    for perturb_idx in range(n_perturbations):
        perturbed = grid.copy()
        chosen_idx = rng.choice(len(free_indices), size=perturb_count, replace=False)
        for idx in chosen_idx:
            y, x = free_indices[idx]
            if (x, y) != start and (x, y) != target:
                perturbed[y, x] = 1
        try:
            algo = algorithm_factory(
                seed=_run_seed(seed, 99, perturb_idx),
                time_budget_s=time_budget_s,
            )
            result = algo.search(perturbed, start, target)
        except Exception:
            result = {"success": False}
        valid, _, _ = validate_path(
            perturbed,
            result.get("path", []) or [],
            start,
            target,
            allow_line_segments=(algorithm_name == "混合优化算法"),
        )
        if result.get("success", False) and valid:
            successes += 1

    return round(successes / n_perturbations, 4)


def evaluate_algorithm(
    algorithm_factory,
    grid: np.ndarray,
    start: tuple,
    target: tuple,
    n_runs: int = 5,
    compute_limit: str = "medium",
    base_seed: int = 0,
    algo_index: int = 0,
    time_budget_s: float = None,
    algorithm_name: str = "",
) -> dict:
    """对单种算法运行多次，统计 10 项指标，并保留逐次原始明细。

    algorithm_factory: callable(seed, time_budget_s) -> 算法实例（每次运行新建，
        保证算法内部 RNG 由 per-run 种子控制）。
    每次运行的种子 = base_seed + algo_index*100 + run_idx，确定性派生。
    time_budget_s: 显式时间预算，缺省按 compute_limit 从 RUNTIME_BUDGET_S 取。

    返回 dict 在旧 10 维聚合指标基础上新增：
    - runs: 逐次明细列表（seed/runtime/双轨成功/校验原因/几何长度等）
    - success_rate: 独立校验通过率（valid_success 口径）
    - reported_success_rate: 算法自报成功率
    - timeout_rate: 触发时间预算的运行占比
    """
    if time_budget_s is None:
        time_budget_s = RUNTIME_BUDGET_S.get(compute_limit, 0.5)

    times = []
    valid_lengths = []
    valid_turnings = []
    valid_smoothness = []
    valid_safety = []
    valid_expanded = []
    reported_successes = 0
    valid_successes = 0
    timeouts = 0
    runs = []

    for run_idx in range(n_runs):
        run_seed = _run_seed(base_seed, algo_index, run_idx)
        t_start = time.perf_counter()
        try:
            algo = algorithm_factory(seed=run_seed, time_budget_s=time_budget_s)
            result = algo.search(grid, start, target)
        except Exception as exc:
            result = {
                "success": False, "path": [], "path_length": 0,
                "invalid_reason": f"exception:{type(exc).__name__}",
            }
        elapsed = time.perf_counter() - t_start

        path = result.get("path", []) or []
        check = evaluate_run_result(result, grid, start, target, algorithm=algorithm_name)
        reported = check["reported_success"]
        valid = check["valid_success"]

        times.append(elapsed)
        if reported:
            reported_successes += 1
        if valid:
            valid_successes += 1
            valid_lengths.append(check["geometric_length"])
            turning = _count_turning_points(path)
            valid_turnings.append(turning)
            valid_smoothness.append(_smoothness(check["path_nodes"], turning))
            valid_safety.append(check["safety_score"])
            valid_expanded.append(int(result.get("nodes_expanded", 0)))
        if result.get("timeout", False):
            timeouts += 1

        runs.append({
            "run_index": run_idx,
            "seed": run_seed,
            "runtime_s": round(elapsed, 4),
            "time_budget_s": time_budget_s,
            "reported_success": reported,
            "valid_success": valid,
            "invalid_reason": check["invalid_reason"],
            "path_nodes": check["path_nodes"],
            "geometric_length": check["geometric_length"],
            "turning_points": _count_turning_points(path) if valid else 0,
            "safety_score": check["safety_score"],
            "nodes_expanded": int(result.get("nodes_expanded", 0)) if valid else 0,
            "timeout": bool(result.get("timeout", False)),
        })

    avg_time = float(np.mean(times)) if times else 0.0
    avg_length = float(np.mean(valid_lengths)) if valid_lengths else 0.0
    success_rate = valid_successes / n_runs if n_runs else 0.0
    reported_success_rate = reported_successes / n_runs if n_runs else 0.0
    timeout_rate = timeouts / n_runs if n_runs else 0.0
    stability_score = 1.0 - (float(np.std(times)) / (avg_time + 1e-6))
    stability_score = float(np.clip(stability_score, 0.0, 1.0))

    avg_turning = float(np.mean(valid_turnings)) if valid_turnings else 0.0
    avg_smoothness = float(np.mean(valid_smoothness)) if valid_smoothness else 0.0
    avg_safety = float(np.mean(valid_safety)) if valid_safety else 0.0
    avg_expanded = int(np.mean(valid_expanded)) if valid_expanded else 0

    compute_cost = _compute_cost(avg_expanded)

    try:
        robustness = _robustness(
            algorithm_factory, grid, start, target,
            algorithm_name=algorithm_name,
            n_perturbations=3, perturb_ratio=0.05,
            seed=_run_seed(base_seed, algo_index, 99),
            time_budget_s=time_budget_s,
        )
    except Exception:
        robustness = success_rate

    return {
        "avg_time": round(avg_time, 4),
        "avg_path_length": round(avg_length, 1),
        "success_rate": round(success_rate, 2),
        "reported_success_rate": round(reported_success_rate, 2),
        "timeout_rate": round(timeout_rate, 2),
        "stability_score": round(stability_score, 4),
        "smoothness": round(avg_smoothness, 4),
        "safety_score": round(avg_safety, 4),
        "expanded_nodes": avg_expanded,
        "turning_points": int(round(avg_turning)),
        "compute_cost": compute_cost,
        "robustness": robustness,
        "n_runs": n_runs,
        "runs": runs,
    }
