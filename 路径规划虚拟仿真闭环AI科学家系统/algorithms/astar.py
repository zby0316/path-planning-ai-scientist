# algorithms/astar.py — A* 算法

import heapq
import numpy as np


class AStar:
    """A* 路径搜索（曼哈顿距离启发函数）"""

    def search(self, grid: np.ndarray, start: tuple, target: tuple) -> dict:
        h, w = grid.shape
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        nodes_expanded = 0

        while open_set:
            _, current = heapq.heappop(open_set)
            nodes_expanded += 1

            if current == target:
                path = self._reconstruct_path(came_from, current)
                return {
                    "success": True,
                    "path": path,
                    "path_length": len(path),
                    "nodes_expanded": nodes_expanded,
                }

            for dx, dy in directions:
                nx, ny = current[0] + dx, current[1] + dy
                if 0 <= nx < w and 0 <= ny < h and grid[ny, nx] == 0:
                    tentative_g = g_score[current] + 1
                    neighbor = (nx, ny)
                    if tentative_g < g_score.get(neighbor, float("inf")):
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f_score = tentative_g + heuristic(neighbor, target)
                        heapq.heappush(open_set, (f_score, neighbor))

        return {"success": False, "path": [], "path_length": 0, "nodes_expanded": nodes_expanded}

    def _reconstruct_path(self, came_from: dict, current: tuple) -> list:
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def search_with_steps(self, grid: np.ndarray, start: tuple, target: tuple) -> dict:
        """逐步记录 A* 搜索过程，用于 GUI 动画展示。

        返回结构：
        {
            "success": bool,
            "final_path": list,
            "frames": [
                {"visited": set, "frontier": set, "current": tuple, "path": list},
                ...
            ],
            "nodes_expanded": int,
        }
        """
        h, w = grid.shape
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        nodes_expanded = 0
        visited = set()
        frontier = {start}

        frames = []
        frames.append({
            "visited": set(),
            "frontier": set(frontier),
            "current": start,
            "path": [start],
        })

        while open_set:
            _, current = heapq.heappop(open_set)
            if current in visited:
                continue
            visited.add(current)
            frontier.discard(current)
            nodes_expanded += 1

            current_frame_path = self._reconstruct_path(came_from, current) if current in came_from else [current]
            frames.append({
                "visited": set(visited),
                "frontier": set(frontier),
                "current": current,
                "path": current_frame_path,
            })

            if current == target:
                final_path = self._reconstruct_path(came_from, current)
                frames.append({
                    "visited": set(visited),
                    "frontier": set(frontier),
                    "current": current,
                    "path": final_path,
                })
                return {
                    "success": True,
                    "final_path": final_path,
                    "frames": frames,
                    "nodes_expanded": nodes_expanded,
                }

            for dx, dy in directions:
                nx, ny = current[0] + dx, current[1] + dy
                if 0 <= nx < w and 0 <= ny < h and grid[ny, nx] == 0:
                    tentative_g = g_score[current] + 1
                    neighbor = (nx, ny)
                    if tentative_g < g_score.get(neighbor, float("inf")):
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f_score = tentative_g + heuristic(neighbor, target)
                        heapq.heappush(open_set, (f_score, neighbor))
                        if neighbor not in visited:
                            frontier.add(neighbor)

        return {
            "success": False,
            "final_path": [],
            "frames": frames,
            "nodes_expanded": nodes_expanded,
        }
