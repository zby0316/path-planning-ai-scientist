# map/connectivity_checker.py — 连通性检查与地图结构指标

from collections import deque

import numpy as np
from scipy.ndimage import label


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


def free_space_connectivity_ratio(grid: np.ndarray) -> float:
    """自由空间连通率：最大自由连通分量 / 自由格总数，取值 [0, 1]。

    1.0 表示全部自由格连成一片；值越小表示自由空间越破碎。
    """
    free = (grid == 0)
    total_free = int(free.sum())
    if total_free == 0:
        return 0.0
    labeled, n_features = label(free)
    if n_features == 0:
        return 0.0
    sizes = np.bincount(labeled.ravel())
    # sizes[0] 是背景（障碍格）计数，连通分量从 1 开始
    return float(sizes[1:].max() / total_free)


def topology_randomness(grid: np.ndarray) -> float:
    """拓扑随机性：障碍离散程度指标，取值 [0, 1]。

    自由-障碍界面边数 / min(自由格数, 障碍格数)：
    障碍聚合成整块时界面小（趋近 0），障碍散布成孤立单格时界面大（趋近 1）。
    """
    free = (grid == 0)
    obstacle = (grid == 1)
    n_free = int(free.sum())
    n_obs = int(obstacle.sum())
    if n_free == 0 or n_obs == 0:
        return 0.0
    interface = 0
    # 垂直界面 + 水平界面
    interface += int((free[:, :-1] & obstacle[:, 1:]).sum()) + int((free[:, 1:] & obstacle[:, :-1]).sum())
    interface += int((free[:-1, :] & obstacle[1:, :]).sum()) + int((free[1:, :] & obstacle[:-1, :]).sum())
    return float(min(interface / min(n_free, n_obs), 1.0))
