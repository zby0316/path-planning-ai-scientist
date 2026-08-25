# tests/test_map_generator.py

import numpy as np
from map.map_generator import MapGenerator


class TestMapGenerator:
    def test_generate_basic(self):
        gen = MapGenerator(seed=42)
        grid = gen.generate(50, 50, 0.3)
        assert grid.shape == (50, 50)
        assert np.all((grid == 0) | (grid == 1))

    def test_generate_obstacle_ratio(self):
        gen = MapGenerator(seed=42)
        grid = gen.generate(100, 100, 0.4)
        actual_ratio = grid.sum() / grid.size
        assert abs(actual_ratio - 0.4) < 0.05

    def test_generate_dynamic_sequence_shape_and_reserved_points(self):
        gen = MapGenerator(seed=42)
        frames = gen.generate_dynamic_sequence(
            30,
            20,
            0.25,
            dynamic_change_rate=0.10,
            steps=4,
            start=(0, 0),
            target=(29, 19),
        )
        assert len(frames) == 4
        for grid in frames:
            assert grid.shape == (20, 30)
            assert grid[0, 0] == 0
            assert grid[19, 29] == 0
            assert np.all((grid == 0) | (grid == 1))

    def test_generate_dynamic_sequence_zero_rate_is_static(self):
        gen = MapGenerator(seed=42)
        frames = gen.generate_dynamic_sequence(
            20,
            20,
            0.30,
            dynamic_change_rate=0.0,
            steps=3,
            start=(0, 0),
            target=(19, 19),
        )
        assert np.array_equal(frames[0], frames[1])
        assert np.array_equal(frames[1], frames[2])

    def test_generate_dynamic_sequence_reproducible_with_seed(self):
        gen_a = MapGenerator(seed=7)
        gen_b = MapGenerator(seed=7)
        frames_a = gen_a.generate_dynamic_sequence(
            20, 20, 0.25, dynamic_change_rate=0.08, steps=3
        )
        frames_b = gen_b.generate_dynamic_sequence(
            20, 20, 0.25, dynamic_change_rate=0.08, steps=3
        )
        assert all(np.array_equal(a, b) for a, b in zip(frames_a, frames_b))
