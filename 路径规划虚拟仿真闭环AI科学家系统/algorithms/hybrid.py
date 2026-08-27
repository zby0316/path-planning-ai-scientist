# algorithms/hybrid.py — 混合优化算法（A* + 局部搜索优化）

import time

import numpy as np
from algorithms.astar import AStar


class HybridAlgorithm:
    """A* 生成初始路径 + 局部路径平滑优化

    time_budget_s: 总搜索时间预算（秒），A* 阶段使用剩余预算，平滑阶段按同一截止时间中断
    """

    def __init__(self, smooth_iterations: int = 50, time_budget_s: float = None):
        self.astar = AStar()
        self.smooth_iterations = smooth_iterations
        self.time_budget_s = time_budget_s
        self._deadline = None

    def _deadline_exceeded(self) -> bool:
        return self._deadline is not None and time.perf_counter() > self._deadline

    def search(self, grid: np.ndarray, start: tuple, target: tuple) -> dict:
        timeout = False

        if self.time_budget_s is not None:
            self._deadline = time.perf_counter() + self.time_budget_s
            # A* 阶段只分配剩余时间，避免平滑阶段被挤占
            remaining = max(self._deadline - time.perf_counter(), 0.0)
            self.astar.time_budget_s = remaining

        # Phase 1: A* 快速生成初始路径
        result = self.astar.search(grid, start, target)
        if not result["success"]:
            return {
                "success": False,
                "path": [],
                "path_length": 0,
                "nodes_expanded": result.get("nodes_expanded", 0),
                "timeout": result.get("timeout", False),
            }

        # Phase 2: 局部平滑优化
        path = result["path"]
        for _ in range(self.smooth_iterations):
            if self._deadline_exceeded():
                timeout = True
                break
            path = self._smooth(path, grid)

        return {
            "success": True,
            "path": path,
            "path_length": len(path),
            "nodes_expanded": result["nodes_expanded"],
            "timeout": timeout,
        }

    def _smooth(self, path: list, grid: np.ndarray) -> list:
        """尝试移除路径中的冗余点（捷径优化）"""
        if len(path) <= 2:
            return path

        h, w = grid.shape
        i = 0
        new_path = [path[0]]

        while i < len(path) - 1:
            # 从后往前找可直达的最远点
            for j in range(len(path) - 1, i, -1):
                if self._line_of_sight(path[i], path[j], grid):
                    new_path.append(path[j])
                    i = j
                    break
            else:
                i += 1
                if i < len(path):
                    new_path.append(path[i])

        return new_path

    def _line_of_sight(self, a: tuple, b: tuple, grid: np.ndarray) -> bool:
        """检查两点之间是否有视线（无障碍物）"""
        x0, y0 = a
        x1, y1 = b
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        h, w = grid.shape
        while (x0, y0) != (x1, y1):
            if not (0 <= x0 < w and 0 <= y0 < h):
                return False
            if grid[y0, x0] == 1:
                return False
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

        return True
