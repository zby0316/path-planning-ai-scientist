# map/connectivity_checker.py — 连通性检查

from collections import deque
import numpy as np


class ConnectivityChecker:
    """使用 BFS 检查起点到终点的连通性"""

    def is_reachable(
        self,
        grid: np.ndarray,
        start: tuple,
        target: tuple,
    ) -> bool:
        h, w = grid.shape
        visited = np.zeros_like(grid, dtype=bool)
        queue = deque([start])
        visited[start[1], start[0]] = True

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while queue:
            x, y = queue.popleft()
            if (x, y) == target:
                return True

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    if not visited[ny, nx] and grid[ny, nx] == 0:
                        visited[ny, nx] = True
                        queue.append((nx, ny))

        return False
