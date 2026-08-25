# map/map_generator.py — 随机栅格地图生成器

import numpy as np


class MapGenerator:
    """生成指定尺寸和障碍物占比的二维栅格地图

    0 = 可通行, 1 = 障碍物
    """

    def __init__(self, seed=None):
        self.rng = np.random.RandomState(seed)

    def generate(
        self,
        width: int,
        height: int,
        obstacle_ratio: float,
        start: tuple = None,
        target: tuple = None,
    ) -> np.ndarray:
        grid = np.zeros((height, width), dtype=np.int8)

        total_cells = width * height
        obstacle_count = int(total_cells * obstacle_ratio)

        all_indices = list(range(total_cells))

        # 保留起点和终点为空
        reserved = set()
        if start:
            reserved.add(start[1] * width + start[0])
        if target:
            reserved.add(target[1] * width + target[0])

        available = [i for i in all_indices if i not in reserved]
        chosen = self.rng.choice(available, size=min(obstacle_count, len(available)), replace=False)

        for idx in chosen:
            row, col = divmod(idx, width)
            grid[row, col] = 1

        return grid

    def perturb_dynamic_obstacles(
        self,
        grid: np.ndarray,
        dynamic_change_rate: float,
        start: tuple = None,
        target: tuple = None,
    ) -> np.ndarray:
        """基于上一帧地图生成动态障碍扰动，保留起点和终点可通行。"""
        if not isinstance(grid, np.ndarray):
            grid = np.asarray(grid, dtype=np.int8)
        if grid.ndim != 2:
            raise ValueError("grid 必须是二维数组")

        rate = float(dynamic_change_rate or 0.0)
        if rate <= 0:
            return grid.copy()
        if rate > 1:
            raise ValueError("dynamic_change_rate 必须在 0 到 1 之间")

        next_grid = grid.copy()
        height, width = next_grid.shape
        mutable_mask = np.ones((height, width), dtype=bool)
        for point in (start, target):
            if point is None:
                continue
            x, y = int(point[0]), int(point[1])
            if 0 <= x < width and 0 <= y < height:
                mutable_mask[y, x] = False
                next_grid[y, x] = 0

        mutable_count = int(np.count_nonzero(mutable_mask))
        if mutable_count <= 0:
            return next_grid

        change_count = max(1, int(round(mutable_count * rate)))
        free_cells = np.argwhere((next_grid == 0) & mutable_mask)
        obstacle_cells = np.argwhere((next_grid == 1) & mutable_mask)

        if len(free_cells) > 0 and len(obstacle_cells) > 0:
            swap_count = max(1, change_count // 2)
            swap_count = min(swap_count, len(free_cells), len(obstacle_cells))
            add_idx = self.rng.choice(len(free_cells), size=swap_count, replace=False)
            remove_idx = self.rng.choice(len(obstacle_cells), size=swap_count, replace=False)
            for y, x in free_cells[add_idx]:
                next_grid[y, x] = 1
            for y, x in obstacle_cells[remove_idx]:
                next_grid[y, x] = 0
        elif len(free_cells) > 0:
            add_count = min(change_count, len(free_cells))
            add_idx = self.rng.choice(len(free_cells), size=add_count, replace=False)
            for y, x in free_cells[add_idx]:
                next_grid[y, x] = 1
        elif len(obstacle_cells) > 0:
            remove_count = min(change_count, len(obstacle_cells))
            remove_idx = self.rng.choice(len(obstacle_cells), size=remove_count, replace=False)
            for y, x in obstacle_cells[remove_idx]:
                next_grid[y, x] = 0

        return next_grid

    def generate_dynamic_sequence(
        self,
        width: int,
        height: int,
        obstacle_ratio: float,
        dynamic_change_rate: float,
        steps: int = 5,
        start: tuple = None,
        target: tuple = None,
    ) -> list:
        """生成动态栅格地图序列，用于虚拟仿真闭环实验。"""
        steps = max(1, int(steps))
        base_grid = self.generate(width, height, obstacle_ratio, start, target)
        frames = [base_grid.copy()]
        current = base_grid
        for _ in range(1, steps):
            current = self.perturb_dynamic_obstacles(
                current,
                dynamic_change_rate=dynamic_change_rate,
                start=start,
                target=target,
            )
            frames.append(current.copy())
        return frames
