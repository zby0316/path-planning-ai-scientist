# tests/test_path_validator.py — 独立路径校验回归

import numpy as np

from evaluation.path_validator import (
    bresenham_cells,
    evaluate_run_result,
    geometric_length,
    safety_score,
    validate_path,
)


def _grid_with_wall(size=10, wall_x=5):
    grid = np.zeros((size, size), dtype=int)
    grid[:, wall_x] = 1  # 竖墙，留 (wall_x, 9) 缺口
    grid[9, wall_x] = 0
    return grid


class TestValidatePath:
    def test_empty_path(self):
        grid = np.zeros((5, 5), dtype=int)
        valid, reason, _ = validate_path(grid, [], (0, 0), (4, 4))
        assert valid is False and reason == "empty_path"

    def test_wrong_start(self):
        grid = np.zeros((5, 5), dtype=int)
        path = [(1, 0), (2, 0)]
        valid, reason, _ = validate_path(grid, path, (0, 0), (4, 4))
        assert valid is False and reason == "wrong_start"

    def test_wrong_target(self):
        grid = np.zeros((5, 5), dtype=int)
        path = [(0, 0), (1, 0)]
        valid, reason, _ = validate_path(grid, path, (0, 0), (4, 4))
        assert valid is False and reason == "wrong_target"

    def test_collision(self):
        grid = _grid_with_wall()
        # 直穿墙（线段模式）必须碰撞
        path = [(0, 4), (9, 4)]
        valid, reason, _ = validate_path(grid, path, (0, 4), (9, 4), allow_line_segments=True)
        assert valid is False and reason == "collision"

    def test_non_adjacent_rejected_for_grid_algo(self):
        grid = np.zeros((5, 5), dtype=int)
        path = [(0, 0), (2, 0), (4, 4)]
        valid, reason, _ = validate_path(grid, path, (0, 0), (4, 4))
        assert valid is False and reason == "non_adjacent_segment"

    def test_line_segment_allowed_for_hybrid(self):
        grid = np.zeros((5, 5), dtype=int)
        path = [(0, 0), (4, 4)]
        valid, reason, _ = validate_path(grid, path, (0, 0), (4, 4), allow_line_segments=True)
        assert valid is True and reason == ""

    def test_valid_adjacent_path(self):
        grid = np.zeros((5, 5), dtype=int)
        path = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)]
        valid, reason, expanded = validate_path(grid, path, (0, 0), (4, 4))
        assert valid is True
        assert len(expanded) == len(path)

    def test_out_of_bounds(self):
        grid = np.zeros((5, 5), dtype=int)
        # 用线段模式绕过邻接检查，构造越界段
        path = [(0, 0), (10, 10)]
        valid, reason, _ = validate_path(grid, path, (0, 0), (10, 10), allow_line_segments=True)
        assert valid is False and reason == "out_of_bounds"

    def test_bresenham_straight(self):
        assert bresenham_cells((0, 0), (3, 0)) == [(0, 0), (1, 0), (2, 0), (3, 0)]
        assert bresenham_cells((0, 0), (0, 0)) == [(0, 0)]

    def test_geometric_length(self):
        assert geometric_length([(0, 0), (3, 4)]) == 5.0
        assert geometric_length([]) == 0.0

    def test_safety_score_positive_on_free_grid(self):
        grid = np.zeros((10, 10), dtype=int)
        grid[0, :] = 1  # 顶行障碍
        s = safety_score(grid, [(5, 5)])
        assert s > 0

    def test_evaluate_run_result_integrity_triple(self):
        grid = np.zeros((5, 5), dtype=int)
        # 算法谎报 success 但路径不合法
        result = {"success": True, "path": [(1, 1), (3, 3)]}
        check = evaluate_run_result(result, grid, (0, 0), (4, 4), algorithm="ACO")
        assert check["reported_success"] is True
        assert check["valid_success"] is False
        assert check["invalid_reason"] == "wrong_start"
        assert check["geometric_length"] is None

        # 合法路径：双轨一致
        good = {"success": True, "path": [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)]}
        check2 = evaluate_run_result(good, grid, (0, 0), (4, 0), algorithm="A*")
        assert check2["valid_success"] is True
        assert check2["invalid_reason"] == ""
        assert check2["geometric_length"] == 4.0
