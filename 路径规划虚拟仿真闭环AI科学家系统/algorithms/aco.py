# algorithms/aco.py — 蚁群算法

import time

import numpy as np


class AntColony:
    """基础蚁群算法路径搜索

    seed: 内部随机数生成器种子，None 时使用系统熵（不可复现）
    time_budget_s: 搜索时间预算（秒），超时后停止迭代并返回当前最优解
    """

    def __init__(
        self,
        n_ants: int = 50,
        n_iterations: int = 100,
        evaporation_rate: float = 0.1,
        alpha: float = 1.0,
        beta: float = 2.0,
        q0: float = 0.9,
        seed: int = None,
        time_budget_s: float = None,
    ):
        self.n_ants = n_ants
        self.n_iterations = n_iterations
        self.evaporation_rate = evaporation_rate
        self.alpha = alpha    # 信息素重要程度
        self.beta = beta      # 启发式重要程度
        self.q0 = q0          # 伪随机比例
        self.seed = seed
        self.time_budget_s = time_budget_s
        self._rng = np.random.RandomState(seed)
        self._deadline = None

    def _deadline_exceeded(self) -> bool:
        return self._deadline is not None and time.perf_counter() > self._deadline

    def search(self, grid: np.ndarray, start: tuple, target: tuple) -> dict:
        h, w = grid.shape
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        pheromone = np.ones((h, w)) * 0.1
        best_path = []
        best_length = float("inf")
        ant_steps = 0
        timeout = False

        if self.time_budget_s is not None:
            self._deadline = time.perf_counter() + self.time_budget_s

        for iteration in range(self.n_iterations):
            if self._deadline_exceeded():
                timeout = True
                break
            all_paths = []
            for _ in range(self.n_ants):
                path, steps = self._construct_path(grid, start, target, pheromone, directions)
                ant_steps += steps
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
            "nodes_expanded": ant_steps,
            "timeout": timeout,
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
            chosen_idx = self._rng.choice(len(candidates), p=probs)
            current = candidates[chosen_idx][0]
            path.append(current)
            visited.add(current)

        return (path if current == target else []), steps
