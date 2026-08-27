# algorithms/sa.py — 模拟退火算法

import math
import time

import numpy as np


class SimulatedAnnealing:
    """模拟退火路径搜索

    seed: 内部随机数生成器种子，None 时使用系统熵（不可复现）
    time_budget_s: 搜索时间预算（秒），超时后停止退火并返回当前最优解
    """

    def __init__(
        self,
        initial_temp: float = 1000.0,
        cooling_rate: float = 0.995,
        min_temp: float = 0.01,
        max_iter_per_temp: int = 50,
        seed: int = None,
        time_budget_s: float = None,
    ):
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp
        self.max_iter_per_temp = max_iter_per_temp
        self.seed = seed
        self.time_budget_s = time_budget_s
        self._rng = np.random.RandomState(seed)
        self._deadline = None

    def _deadline_exceeded(self) -> bool:
        return self._deadline is not None and time.perf_counter() > self._deadline

    def search(self, grid: np.ndarray, start: tuple, target: tuple) -> dict:
        h, w = grid.shape
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        neighbor_evals = 0
        timeout = False

        if self.time_budget_s is not None:
            self._deadline = time.perf_counter() + self.time_budget_s

        def random_path():
            current = start
            path = [current]
            visited = set([current])
            for _ in range(w * h):
                if current == target:
                    break
                x, y = current
                neighbors = []
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and grid[ny, nx] == 0:
                        neighbors.append((nx, ny))
                if not neighbors:
                    break
                neighbors.sort(key=lambda n: (n in visited, abs(n[0] - target[0]) + abs(n[1] - target[1])))
                current = neighbors[0]
                visited.add(current)
                path.append(current)
            return path

        def energy(p):
            if not p or p[-1] != target:
                return float("inf")
            return len(p)

        def neighbor(p):
            if len(p) < 3:
                return p
            idx = self._rng.randint(1, len(p) - 1)
            x, y = p[idx]
            candidates = []
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and grid[ny, nx] == 0:
                    candidates.append((nx, ny))
            if candidates:
                new_node = candidates[self._rng.randint(len(candidates))]
                return p[:idx] + [new_node] + p[idx + 1:]
            return p

        current_path = random_path()
        current_energy = energy(current_path)
        best_path = current_path
        best_energy = current_energy

        temp = self.initial_temp
        while temp > self.min_temp:
            if self._deadline_exceeded():
                timeout = True
                break
            for _ in range(self.max_iter_per_temp):
                neighbor_evals += 1
                new_path = neighbor(current_path)
                new_energy = energy(new_path)
                delta = new_energy - current_energy

                if delta < 0 or self._rng.random_sample() < math.exp(-delta / temp):
                    current_path = new_path
                    current_energy = new_energy

                    if current_energy < best_energy:
                        best_path = current_path
                        best_energy = current_energy

            temp *= self.cooling_rate

        success = best_path[-1] == target if best_path else False
        return {
            "success": success,
            "path": best_path,
            "path_length": len(best_path),
            "nodes_expanded": neighbor_evals,
            "timeout": timeout,
        }
