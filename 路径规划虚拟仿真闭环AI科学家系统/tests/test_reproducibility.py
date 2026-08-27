# tests/test_reproducibility.py — 种子贯通可复现性回归

import numpy as np

from algorithms.aco import AntColony
from algorithms.pso import ParticleSwarm
from algorithms.sa import SimulatedAnnealing
from map.map_generator import MapGenerator


def _make_grid(seed=123, size=20, ratio=0.2):
    gen = MapGenerator(seed=seed)
    return gen.generate(size, size, ratio, (0, 0), (size - 1, size - 1))


class TestSeedReproducibility:
    def test_aco_same_seed_same_path(self):
        grid = _make_grid()
        r1 = AntColony(n_ants=5, n_iterations=3, seed=7).search(grid, (0, 0), (19, 19))
        r2 = AntColony(n_ants=5, n_iterations=3, seed=7).search(grid, (0, 0), (19, 19))
        assert r1["path"] == r2["path"]
        assert r1["success"] == r2["success"]
        assert r1["nodes_expanded"] == r2["nodes_expanded"]

    def test_pso_same_seed_same_path(self):
        grid = _make_grid()
        r1 = ParticleSwarm(n_particles=5, n_iterations=5, seed=7).search(grid, (0, 0), (19, 19))
        r2 = ParticleSwarm(n_particles=5, n_iterations=5, seed=7).search(grid, (0, 0), (19, 19))
        assert r1["path"] == r2["path"]
        assert r1["nodes_expanded"] == r2["nodes_expanded"]

    def test_sa_same_seed_same_path(self):
        grid = _make_grid()
        sa_kw = {"initial_temp": 100.0, "cooling_rate": 0.9, "max_iter_per_temp": 3, "seed": 7}
        r1 = SimulatedAnnealing(**sa_kw).search(grid, (0, 0), (19, 19))
        r2 = SimulatedAnnealing(**sa_kw).search(grid, (0, 0), (19, 19))
        assert r1["path"] == r2["path"]
        assert r1["nodes_expanded"] == r2["nodes_expanded"]

    def test_different_seed_can_differ(self):
        """不同种子应有机会产生不同结果（即种子确实在驱动 RNG）。"""
        grid = _make_grid(seed=5, size=30, ratio=0.25)
        results = set()
        for seed in range(6):
            r = AntColony(n_ants=5, n_iterations=3, seed=seed).search(grid, (0, 0), (29, 29))
            results.add((r["success"], len(r["path"]), r["nodes_expanded"]))
        assert len(results) > 1

    def test_evaluate_algorithm_seed_derivation(self):
        """种子派生公式：base + algo_index*100 + run_idx。"""
        from evaluation.metrics import _run_seed
        assert _run_seed(100, 2, 3) == 100 + 200 + 3
        assert _run_seed(0, 0, 0) == 0
        # 不同算法/重复不碰撞
        seeds = [_run_seed(50, a, r) for a in range(5) for r in range(5)]
        assert len(seeds) == len(set(seeds))
