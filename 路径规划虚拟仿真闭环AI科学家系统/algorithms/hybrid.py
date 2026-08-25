# algorithms/hybrid.py — 混合优化算法（A* + 局部搜索优化）

import numpy as np
from algorithms.astar import AStar


class HybridAlgorithm:
    """A* 生成初始路径 + 局部路径平滑优化"""

    def __init__(self):
        self.astar = AStar()
        self.smooth_iterations = 50

    def search(self, grid: np.ndarray, start: tuple, target: tuple) -> dict:
        # Phase 1: A* 快速生成初始路径
        result = self.astar.search(grid, start, target)
        if not result["success"]:
            return result

        # Phase 2: 局部平滑优化
        path = result["path"]
        for _ in range(self.smooth_iterations):
            path = self._smooth(path, grid)

        return {
            "success": True,
            "path": path,
            "path_length": len(path),
            "nodes_expanded": result["nodes_expanded"],
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
