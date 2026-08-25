# algorithms/pso.py — 粒子群算法

import numpy as np
from collections import deque


class ParticleSwarm:
    """基础粒子群路径搜索"""

    def __init__(self, n_particles: int = 30, n_iterations: int = 200):
        self.n_particles = n_particles
        self.n_iterations = n_iterations
        self.w = 0.5        # 惯性权重
        self.c1 = 1.5       # 个体学习因子
        self.c2 = 1.5       # 群体学习因子

    def search(self, grid: np.ndarray, start: tuple, target: tuple) -> dict:
        h, w = grid.shape
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        def random_path():
            """生成随机可行路径"""
            path = [start]
            visited = set([start])
            current = start
            for _ in range(w * h):
                if current == target:
                    break
                neighbors = []
                x, y = current
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and grid[ny, nx] == 0:
                        dist = abs(nx - target[0]) + abs(ny - target[1])
                        neighbors.append(((nx, ny), dist))
                if not neighbors:
                    break
                neighbors.sort(key=lambda v: v[1] + (0 if (v[0] not in visited) else 1000))
                best_neighbor = neighbors[0][0]
                visited.add(best_neighbor)
                path.append(best_neighbor)
                current = best_neighbor
            return path

        particles = [random_path() for _ in range(self.n_particles)]
        p_best = [p for p in particles]
        g_best = min(particles, key=lambda p: self._fitness(p, target))

        for _ in range(self.n_iterations):
            for i in range(self.n_particles):
                new_path = self._update_path(
                    particles[i], p_best[i], g_best, grid, start, target, directions
                )
                if self._fitness(new_path, target) < self._fitness(particles[i], target):
                    particles[i] = new_path
                if self._fitness(new_path, target) < self._fitness(p_best[i], target):
                    p_best[i] = new_path
                if self._fitness(new_path, target) < self._fitness(g_best, target):
                    g_best = new_path

        success = g_best[-1] == target if g_best else False
        return {
            "success": success,
            "path": g_best,
            "path_length": len(g_best),
        }

    def _fitness(self, path: list, target: tuple) -> float:
        if not path:
            return float("inf")
        dist = abs(path[-1][0] - target[0]) + abs(path[-1][1] - target[1])
        return len(path) + dist * 10

    def _update_path(self, path, p_best, g_best, grid, start, target, directions):
        """交叉变异更新路径"""
        h, w = grid.shape
        r = np.random.random()
        if r < self.w:    # 保持原路径
            return self._mutate(path, grid, directions)
        elif r < self.w + self.c1 / (self.c1 + self.c2 + self.w):
            return self._crossover(path, p_best, grid, start)
        else:
            return self._crossover(path, g_best, grid, start)

    def _crossover(self, path_a, path_b, grid, start):
        if len(path_b) < 2:
            return path_a
        idx = np.random.randint(0, min(len(path_a), len(path_b)))
        new_path = path_a[:idx] + path_b[idx:]
        if new_path[0] != start:
            new_path.insert(0, start)
        return new_path

    def _mutate(self, path, grid, directions):
        if len(path) < 3:
            return path
        idx = np.random.randint(1, len(path) - 1)
        x, y = path[idx]
        h, w = grid.shape
        candidates = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and grid[ny, nx] == 0:
                candidates.append((nx, ny))
        if candidates:
            new_node = candidates[np.random.randint(len(candidates))]
            new_path = path[:idx] + [new_node] + path[idx + 1:]
            return new_path
        return path
