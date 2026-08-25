# algorithms/aco.py — 蚁群算法

import numpy as np


class AntColony:
    """基础蚁群算法路径搜索"""

    def __init__(self):
        self.n_ants = 50
        self.n_iterations = 100
        self.evaporation_rate = 0.1
        self.alpha = 1.0    # 信息素重要程度
        self.beta = 2.0     # 启发式重要程度
        self.q0 = 0.9       # 伪随机比例

    def search(self, grid: np.ndarray, start: tuple, target: tuple) -> dict:
        h, w = grid.shape
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        pheromone = np.ones((h, w)) * 0.1
        best_path = []
        best_length = float("inf")

        for iteration in range(self.n_iterations):
            all_paths = []
            for _ in range(self.n_ants):
                path = self._construct_path(grid, start, target, pheromone, directions)
                if path:
                    all_paths.append(path)
                    if len(path) < best_length:
                        best_length = len(path)
                        best_path = path

            # 信息素挥发
            pheromone *= (1 - self.evaporation_rate)
            # 信息素沉积
            for path in all_paths:
                deposit = 1.0 / len(path)
                for x, y in path:
                    pheromone[y, x] += deposit

        success = len(best_path) > 0
        return {
            "success": success,
            "path": best_path,
            "path_length": len(best_path),
        }

    def _construct_path(self, grid, start, target, pheromone, directions):
        h, w = grid.shape
        current = start
        path = [current]
        visited = set([current])
        steps = 0
        max_steps = w * h * 2

        while current != target and steps < max_steps:
            steps += 1
            x, y = current
            candidates = []
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and grid[ny, nx] == 0 and (nx, ny) not in visited:
                    heuristic = 1.0 / (abs(nx - target[0]) + abs(ny - target[1]) + 1)
                    prob = (pheromone[ny, nx] ** self.alpha) * (heuristic ** self.beta)
                    candidates.append(((nx, ny), prob))

            if not candidates:
                break

            total = sum(p for _, p in candidates)
            probs = [p / total for _, p in candidates]
            chosen_idx = np.random.choice(len(candidates), p=probs)
            current = candidates[chosen_idx][0]
            path.append(current)
            visited.add(current)

        return path if current == target else []
