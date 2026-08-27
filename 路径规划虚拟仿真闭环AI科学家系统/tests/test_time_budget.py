# tests/test_time_budget.py — 时间预算真正生效回归

import time

from algorithms.aco import AntColony
from algorithms.astar import AStar
from algorithms.hybrid import HybridAlgorithm
from algorithms.pso import ParticleSwarm
from algorithms.sa import SimulatedAnnealing
from map.map_generator import MapGenerator


def _make_grid(seed=42, size=30, ratio=0.25):
    gen = MapGenerator(seed=seed)
    return gen.generate(size, size, ratio, (0, 0), (size - 1, size - 1))


class TestTimeBudget:
    def test_sa_budget_bounds_runtime(self):
        """SA 温度循环无迭代上限，必须被时间预算截断。"""
        grid = _make_grid()
        t0 = time.perf_counter()
        r = SimulatedAnnealing(seed=1, time_budget_s=0.2).search(grid, (0, 0), (29, 29))
        elapsed = time.perf_counter() - t0
        assert elapsed < 1.5  # 预算 0.2s + 少量开销
        assert r["timeout"] is True

    def test_aco_budget_bounds_runtime(self):
        grid = _make_grid()
        t0 = time.perf_counter()
        r = AntColony(seed=1, n_iterations=100000, time_budget_s=0.1).search(grid, (0, 0), (29, 29))
        elapsed = time.perf_counter() - t0
        assert elapsed < 1.0
        assert r["timeout"] is True

    def test_pso_budget_bounds_runtime(self):
        grid = _make_grid()
        t0 = time.perf_counter()
        r = ParticleSwarm(seed=1, n_iterations=100000, time_budget_s=0.1).search(grid, (0, 0), (29, 29))
        elapsed = time.perf_counter() - t0
        assert elapsed < 1.0
        assert r["timeout"] is True

    def test_astar_timeout_flag(self):
        """A* 超小预算应中断并打 timeout 标记，而非挂死。"""
        grid = _make_grid(seed=9, size=60, ratio=0.3)
        r = AStar(time_budget_s=0.000001).search(grid, (0, 0), (59, 59))
        assert r["timeout"] is True

    def test_hybrid_budget_passthrough(self):
        grid = _make_grid()
        r = HybridAlgorithm(time_budget_s=0.000001).search(grid, (0, 0), (29, 29))
        assert r.get("timeout") is True

    def test_no_budget_completes(self):
        grid = _make_grid()
        r = AStar().search(grid, (0, 0), (29, 29))
        assert r["success"] is True
        assert r["timeout"] is False

    def test_runtime_budget_config(self):
        from config import RUNTIME_BUDGET_S
        assert set(RUNTIME_BUDGET_S.keys()) == {"low", "medium", "high"}
        assert RUNTIME_BUDGET_S["low"] < RUNTIME_BUDGET_S["medium"] < RUNTIME_BUDGET_S["high"]
