# algorithms/pso.py — 粒子群算法

import time

import numpy as np
from collections import deque


class ParticleSwarm:
    """基础粒子群路径搜索

    seed: 内部随机数生成器种子，None 时使用系统熵（不可复现）
    time_budget_s: 搜索时间预算（秒），超时后停止迭代并返回当前最优解
    """

    def __init__(
        self,
        n_particles: int = 30,
        n_iterations: int = 200,
        w: float = 0.5,
        c1: float = 1.5,
        c2: float = 1.5,
        seed: int = None,
        time_budget_s: float = None,
    ):
        self.n_particles = n_particles
        self.n_iterations = n_iterations
        self.w = w          # 惯性权重
        self.c1 = c1        # 个体学习因子
        self.c2 = c2        # 群体学习因子
        self.seed = seed
        self.time_budget_s = time_budget_s
        self._rng = np.random.RandomState(seed)
        self._deadline = None

    def _deadline_exceeded(self) -> bool:
        return self._deadline is not None and time.perf_counter() > self._deadline

    def search(self, grid: np.ndarray, start: tuple, target: tuple) -> dict:
        h, w = grid.shape
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        fitness_evals = 0
        timeout = False

        if self.time_budget_s is not None:
            self._deadline = time.perf_counter() + self.time_budget_s

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
        fitness_evals += self.n_particles
        g_best = min(particles, key=lambda p: self._fitness(p, target))

        for _ in range(self.n_iterations):
            if self._deadline_exceeded():
                timeout = True
                break
            for i in range(self.n_particles):
                if i % 5 == 0 and self._deadline_exceeded():
                    # 单次迭代在大幅地图上可能远超预算，内层周期性检查
                    timeout = True
                    break
                new_path = self._update_path(
                    particles[i], p_best[i], g_best, grid, start, target, directions
                )
                fitness_evals += 3
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
            "nodes_expanded": fitness_evals,
            "timeout": timeout,
        }

    def _fitness(self, path: list, target: tuple) -> float:
        if not path:
            return float("inf")
        dist = abs(path[-1][0] - target[0]) + abs(path[-1][1] - target[1])
        return len(path) + dist * 10

    def _update_path(self, path, p_best, g_best, grid, start, target, directions):
        """交叉变异更新路径"""
        h, w = grid.shape
        r = self._rng.random_sample()
        if r < self.w:    # 保持原路径
            return self._mutate(path, grid, directions)
        elif r < self.w + self.c1 / (self.c1 + self.c2 + self.w):
            return self._crossover(path, p_best, grid, start)
        else:
            return self._crossover(path, g_best, grid, start)

    def _crossover(self, path_a, path_b, grid, start):
        if len(path_b) < 2:
            return path_a
        idx = self._rng.randint(0, min(len(path_a), len(path_b)))
        new_path = path_a[:idx] + path_b[idx:]
        if new_path[0] != start:
            new_path.insert(0, start)
        return new_path

    def _mutate(self, path, grid, directions):
        if len(path) < 3:
            return path
        idx = self._rng.randint(1, len(path) - 1)
        x, y = path[idx]
        h, w = grid.shape
        candidates = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and grid[ny, nx] == 0:
                candidates.append((nx, ny))
        if candidates:
            new_node = candidates[self._rng.randint(len(candidates))]
            new_path = path[:idx] + [new_node] + path[idx + 1:]
            return new_path
        return path
