# evaluation/path_validator.py — 独立路径合法性校验
#
# 不信任算法自报的 success：对返回路径做独立的起终点/邻接/碰撞/越界校验，
# 产出 reported_success / valid_success / invalid_reason 三件套。
# 校验逻辑移植自 evidence/validated_experiments 的旁路验证脚本，保持口径一致。

import math

import numpy as np
from scipy.ndimage import distance_transform_edt


def bresenham_cells(a: tuple, b: tuple) -> list:
    """Bresenham 直线栅格化：返回 a→b 途经的全部栅格坐标。"""
    x0, y0 = a
    x1, y1 = b
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    cells = [(x0, y0)]
    while (x0, y0) != (x1, y1):
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
        cells.append((x0, y0))
    return cells


def validate_path(
    grid: np.ndarray,
    path: list,
    start: tuple,
    target: tuple,
    allow_line_segments: bool = False,
):
    """校验路径合法性。

    allow_line_segments: 允许非相邻的直线段（混合优化算法平滑后的路径形态）；
        即便允许，每段仍做 Bresenham 逐格碰撞检查。
    返回 (valid: bool, invalid_reason: str, expanded_cells: list)。
    """
    if not path:
        return False, "empty_path", []
    points = [tuple(int(v) for v in p) for p in path]
    if points[0] != start:
        return False, "wrong_start", []
    if points[-1] != target:
        return False, "wrong_target", []
    h, w = grid.shape
    expanded = [points[0]]
    for a, b in zip(points[:-1], points[1:]):
        if not allow_line_segments and abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1:
            return False, "non_adjacent_segment", []
        cells = bresenham_cells(a, b)
        for x, y in cells:
            if not (0 <= x < w and 0 <= y < h):
                return False, "out_of_bounds", []
            if grid[y, x] == 1:
                return False, "collision", []
        expanded.extend(cells[1:])
    return True, "", expanded


def geometric_length(path: list) -> float:
    """几何长度：逐段欧氏距离之和（独立于算法自报的 path_length）。"""
    if not path:
        return 0.0
    return float(
        sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path[:-1], path[1:]))
    )


def safety_score(grid: np.ndarray, expanded_path: list) -> float:
    """EDT 安全距离：路径各格到最近障碍的平均距离，按地图尺度归一化。"""
    if not expanded_path:
        return 0.0
    distance = distance_transform_edt(grid == 0)
    values = [float(distance[y, x]) for x, y in expanded_path]
    return float(np.mean(values) / max(grid.shape))


def evaluate_run_result(
    result: dict,
    grid: np.ndarray,
    start: tuple,
    target: tuple,
    algorithm: str = "",
) -> dict:
    """对算法单次运行结果做独立校验，返回入库所需的诚信三件套与重算指标。

    返回字段：reported_success / valid_success / invalid_reason /
    geometric_length / safety_score / path_nodes。
    """
    path = result.get("path", []) or []
    reported = bool(result.get("success", False))
    error = result.get("invalid_reason", "")
    valid, reason, expanded = validate_path(
        grid,
        path,
        start,
        target,
        allow_line_segments=(algorithm == "混合优化算法"),
    )
    valid_success = bool(reported and valid)
    invalid_reason = error or (reason if not valid else "")
    return {
        "reported_success": reported,
        "valid_success": valid_success,
        "invalid_reason": invalid_reason,
        "geometric_length": geometric_length(path) if valid_success else None,
        "safety_score": safety_score(grid, expanded) if valid_success else 0.0,
        "path_nodes": len(path),
    }
