# evaluation/metrics.py — 性能指标计算（10 维扩展版）

import math
import time

import numpy as np
from scipy.ndimage import distance_transform_edt


LOW_COMPUTE_RUNTIME_BUDGET = {
    "low": 0.05,
    "medium": 0.5,
    "high": 2.0,
}


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
    raw = expanded_nodes * math.log(expanded_nodes + 1) / 10000.0
    return round(min(max(raw, 0.0), 1.0), 4)


def _robustness(
    algorithm_func,
    grid: np.ndarray,
    start: tuple,
    target: tuple,
    n_perturbations: int = 3,
    perturb_ratio: float = 0.05,
    seed: int = 0,
) -> float:
    h, w = grid.shape
    rng = np.random.RandomState(seed)
    free_indices = np.argwhere(grid == 0)
    if len(free_indices) == 0:
        return 0.0

    successes = 0
    perturb_count = max(1, int(len(free_indices) * perturb_ratio))
    for _ in range(n_perturbations):
        perturbed = grid.copy()
        chosen_idx = rng.choice(len(free_indices), size=perturb_count, replace=False)
        for idx in chosen_idx:
            y, x = free_indices[idx]
            if (x, y) != start and (x, y) != target:
                perturbed[y, x] = 1
        try:
            result = algorithm_func(perturbed, start, target)
        except Exception:
            result = {"success": False}
        if result.get("success", False):
            successes += 1

    return round(successes / n_perturbations, 4)


def evaluate_algorithm(
    algorithm_func,
    grid: np.ndarray,
    start: tuple,
    target: tuple,
    n_runs: int = 5,
    compute_limit: str = "medium",
) -> dict:
    """对单种算法运行多次，统计 10 项指标"""
    times = []
    lengths = []
    smoothness_list = []
    safety_list = []
    turning_list = []
    expanded_list = []
    successes = 0
    last_result = None

    budget = LOW_COMPUTE_RUNTIME_BUDGET.get(compute_limit, 0.5)

    for run_idx in range(n_runs):
        t_start = time.perf_counter()
        try:
            result = algorithm_func(grid, start, target)
        except Exception:
            result = {"success": False, "path": [], "path_length": 0}
        elapsed = time.perf_counter() - t_start
        last_result = result

        times.append(elapsed)
        if result.get("success", False):
            successes += 1
            path = result.get("path", []) or []
            lengths.append(result.get("path_length", len(path)))
            turning = _count_turning_points(path)
            turning_list.append(turning)
            smoothness_list.append(_smoothness(len(path), turning))
            safety_list.append(_safety_score(path, grid))
            expanded_list.append(int(result.get("nodes_expanded", 0)))
        else:
            turning_list.append(0)
            smoothness_list.append(1.0)
            safety_list.append(0.0)
            expanded_list.append(0)

    avg_time = float(np.mean(times)) if times else 0.0
    avg_length = float(np.mean(lengths)) if lengths else 0.0
    success_rate = successes / n_runs if n_runs else 0.0
    stability_score = 1.0 - (float(np.std(times)) / (avg_time + 1e-6))
    stability_score = float(np.clip(stability_score, 0.0, 1.0))

    avg_turning = float(np.mean(turning_list)) if turning_list else 0.0
    avg_smoothness = float(np.mean(smoothness_list)) if smoothness_list else 0.0
    avg_safety = float(np.mean(safety_list)) if safety_list else 0.0
    avg_expanded = int(np.mean(expanded_list)) if expanded_list else 0

    compute_cost = _compute_cost(avg_expanded)

    try:
        robustness = _robustness(
            algorithm_func, grid, start, target,
            n_perturbations=3, perturb_ratio=0.05, seed=0,
        )
    except Exception:
        robustness = success_rate

    return {
        "avg_time": round(avg_time, 4),
        "avg_path_length": round(avg_length, 1),
        "success_rate": round(success_rate, 2),
        "stability_score": round(stability_score, 4),
        "smoothness": round(avg_smoothness, 4),
        "safety_score": round(avg_safety, 4),
        "expanded_nodes": avg_expanded,
        "turning_points": int(round(avg_turning)),
        "compute_cost": compute_cost,
        "robustness": robustness,
    }
