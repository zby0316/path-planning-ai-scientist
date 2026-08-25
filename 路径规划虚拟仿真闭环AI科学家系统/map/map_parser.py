"""多格式地图解析器。

支持 Moving AI 的 `.map` / `.scen`、CSV 栅格、JSON 栅格、NumPy `.npy` 五种格式，
统一返回 ``{"grid": np.ndarray, "metadata": dict, "tasks": list}`` 结构。
"""
import json
import re
from pathlib import Path

import numpy as np


_OBSTACLE_CHARS = {"@", "O", "T", "W"}


class MapParser:
    """多格式地图与任务场景解析入口。"""

    def parse(self, filepath):
        path = Path(filepath)
        ext = path.suffix.lower()
        if ext == ".map":
            return self._parse_map(path)
        if ext == ".scen":
            return self._parse_scen(path)
        if ext == ".csv":
            return self._parse_csv(path)
        if ext == ".json":
            return self._parse_json(path)
        if ext == ".npy":
            return self._parse_npy(path)
        raise ValueError(f"不支持的地图格式: {ext}")

    def _parse_map(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            raw_lines = f.readlines()

        height = None
        width = None
        map_lines = []
        in_map = False

        for line in raw_lines:
            stripped = line.rstrip("\n").rstrip("\r")
            if not in_map:
                if stripped.lstrip().lower().startswith("height"):
                    height = int(_extract_int(stripped))
                elif stripped.lstrip().lower().startswith("width"):
                    width = int(_extract_int(stripped))
                elif stripped.lstrip().lower().startswith("map"):
                    in_map = True
            else:
                map_lines.append(stripped)

        if height is None or width is None:
            raise ValueError(f"无法从 {filepath} 解析 height / width")

        rows = map_lines[:height]
        grid = np.zeros((height, width), dtype=np.int8)
        for r, row in enumerate(rows):
            for c, ch in enumerate(row[:width]):
                if ch in _OBSTACLE_CHARS:
                    grid[r, c] = 1
                else:
                    grid[r, c] = 0

        result = {
            "grid": grid,
            "metadata": {
                "format": "movingai_map",
                "height": int(height),
                "width": int(width),
            },
            "tasks": [],
        }

        scen_path = _find_scen_for_map(filepath)
        if scen_path is not None and scen_path.exists():
            scen_result = self._parse_scen(scen_path)
            result["tasks"] = scen_result["tasks"]

        return result

    def _parse_scen(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            raw_lines = f.readlines()

        tasks = []
        for line in raw_lines:
            stripped = line.strip()
            if not stripped:
                continue
            parts = stripped.split()
            head = parts[0]
            if head.lower() == "version" or head == "Bucket":
                continue

            if not _is_int(parts[0]):
                parts = parts[1:]

            if len(parts) < 4:
                continue

            if len(parts) >= 5:
                start_x = int(parts[1])
                start_y = int(parts[2])
                target_x = int(parts[3])
                target_y = int(parts[4])
                optimal_length = float(parts[5]) if len(parts) >= 6 else 0.0
            else:
                start_x = int(parts[0])
                start_y = int(parts[1])
                target_x = int(parts[2])
                target_y = int(parts[3])
                optimal_length = 0.0

            tasks.append(
                {
                    "start_x": start_x,
                    "start_y": start_y,
                    "target_x": target_x,
                    "target_y": target_y,
                    "optimal_length": optimal_length,
                }
            )

        return {
            "grid": None,
            "metadata": {"format": "movingai_scen"},
            "tasks": tasks,
        }

    def _parse_csv(self, filepath):
        arr = np.loadtxt(filepath, delimiter=",", dtype=int)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        return {
            "grid": arr,
            "metadata": {"format": "csv"},
            "tasks": [],
        }

    def _parse_json(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        arr = np.array(data, dtype=int)
        return {
            "grid": arr,
            "metadata": {"format": "json"},
            "tasks": [],
        }

    def _parse_npy(self, filepath):
        arr = np.load(filepath)
        return {
            "grid": arr,
            "metadata": {"format": "npy"},
            "tasks": [],
        }


def _extract_int(token):
    matches = re.findall(r"-?\d+", token)
    if not matches:
        raise ValueError(f"无法从 {token!r} 提取整数")
    return matches[0]


def _is_int(token):
    try:
        int(token)
        return True
    except (TypeError, ValueError):
        return False


def _find_scen_for_map(filepath):
    path = Path(filepath)
    candidates = [path.with_name(path.name + ".scen")]
    parent = path.parent
    if parent:
        for match in parent.glob(path.name + ".scen"):
            return match
    for cand in candidates:
        if cand.exists():
            return cand
    return None
