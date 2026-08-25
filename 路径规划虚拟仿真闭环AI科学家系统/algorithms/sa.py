# algorithms/sa.py — 模拟退火算法

import numpy as np
import random
import math


class SimulatedAnnealing:
    """模拟退火路径搜索"""

    def __init__(self):
        self.initial_temp = 1000.0
        self.cooling_rate = 0.995
        self.min_temp = 0.01
        self.max_iter_per_temp = 50

    def search(self, grid: np.ndarray, start: tuple, target: tuple) -> dict:
        h, w = grid.shape
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

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
            idx = random.randint(1, len(p) - 2)
            x, y = p[idx]
            candidates = []
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and grid[ny, nx] == 0:
                    candidates.append((nx, ny))
            if candidates:
                new_node = random.choice(candidates)
                return p[:idx] + [new_node] + p[idx + 1:]
            return p

        current_path = random_path()
        current_energy = energy(current_path)
        best_path = current_path
        best_energy = current_energy

        temp = self.initial_temp
        while temp > self.min_temp:
            for _ in range(self.max_iter_per_temp):
                new_path = neighbor(current_path)
                new_energy = energy(new_path)
                delta = new_energy - current_energy

                if delta < 0 or random.random() < math.exp(-delta / temp):
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
        }
