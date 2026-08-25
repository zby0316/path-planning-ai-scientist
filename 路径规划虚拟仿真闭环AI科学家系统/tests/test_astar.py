# tests/test_astar.py

import numpy as np
from algorithms.astar import AStar


class TestAStar:
    def test_direct_path(self):
        grid = np.zeros((10, 10), dtype=np.int8)
        astar = AStar()
        result = astar.search(grid, (0, 0), (9, 9))
        assert result["success"] is True
        assert result["path_length"] > 0
        assert result["path"][0] == (0, 0)
        assert result["path"][-1] == (9, 9)

    def test_no_path(self):
        grid = np.ones((10, 10), dtype=np.int8)
        grid[0, 0] = 0
        grid[9, 9] = 0
        astar = AStar()
        result = astar.search(grid, (0, 0), (9, 9))
        assert result["success"] is False

    def test_search_with_steps_reachable(self):
        grid = np.zeros((10, 10), dtype=np.int8)
        astar = AStar()
        result = astar.search_with_steps(grid, (0, 0), (9, 9))
        assert result["success"] is True
        assert result["final_path"][0] == (0, 0)
        assert result["final_path"][-1] == (9, 9)
        assert len(result["frames"]) > 1
        first_frame = result["frames"][0]
        assert "visited" in first_frame
        assert "frontier" in first_frame
        assert "current" in first_frame
        assert "path" in first_frame
        assert (0, 0) in first_frame["frontier"]

    def test_search_with_steps_unreachable(self):
        grid = np.ones((10, 10), dtype=np.int8)
        grid[0, 0] = 0
        grid[9, 9] = 0
        astar = AStar()
        result = astar.search_with_steps(grid, (0, 0), (9, 9))
        assert result["success"] is False
        assert result["final_path"] == []
        assert len(result["frames"]) > 0

    def test_search_with_steps_same_point(self):
        grid = np.zeros((10, 10), dtype=np.int8)
        astar = AStar()
        result = astar.search_with_steps(grid, (3, 3), (3, 3))
        assert result["success"] is True
        assert result["final_path"] == [(3, 3)]
        assert result["nodes_expanded"] == 1
