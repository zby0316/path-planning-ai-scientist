# map/map_analyzer.py — 地图特征分析器

import numpy as np

from config import OBSTACLE_LOW_THRESHOLD, OBSTACLE_MEDIUM_THRESHOLD


class MapAnalyzer:
    """对栅格地图进行特征分析，输出复杂度等级与综合指标"""

    def analyze(
        self,
        grid: np.ndarray,
        start: tuple,
        target: tuple,
        connectivity: float = 0.5,
        topology_randomness: float = 0.5,
        dynamic_change_rate: float = 0.0,
    ) -> dict:
        total_cells = int(grid.size)
        obstacle_count = int(np.count_nonzero(grid == 1))
        obstacle_ratio = obstacle_count / total_cells if total_cells > 0 else 0.0
        free_space_ratio = 1.0 - obstacle_ratio

        if obstacle_ratio < OBSTACLE_LOW_THRESHOLD:
            scene_level = "低复杂度"
        elif obstacle_ratio <= OBSTACLE_MEDIUM_THRESHOLD:
            scene_level = "中复杂度"
        else:
            scene_level = "高复杂度"

        complexity_index = (
            0.45 * obstacle_ratio +
            0.25 * (1 - connectivity) +
            0.20 * topology_randomness +
            0.10 * dynamic_change_rate
        )
        complexity_index = round(max(0.0, min(1.0, complexity_index)), 4)

        return {
            "scene_level": scene_level,
            "complexity_index": complexity_index,
            "obstacle_ratio": round(obstacle_ratio, 4),
            "start": start,
            "target": target,
            "free_space_ratio": round(free_space_ratio, 4),
            "total_cells": total_cells,
            # ---- Phase 4 新增字段（提示词 4-2）----
            "cluster_count": 0,
            "bottleneck_count": 0,
            "entropy": 0.0,
            "distance_to_target": _manhattan(start, target),
        }


def _manhattan(a, b) -> int:
    """曼哈顿距离（容错：允许 list / tuple / ndarray）。"""
    try:
        ax, ay = int(a[0]), int(a[1])
        bx, by = int(b[0]), int(b[1])
    except (TypeError, IndexError, ValueError):
        return 0
    return abs(ax - bx) + abs(ay - by)
