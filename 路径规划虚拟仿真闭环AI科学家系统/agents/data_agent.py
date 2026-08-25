# agents/data_agent.py — 数据接收与校验智能体

import logging
from datetime import datetime, timezone

import numpy as np

from config import COMPUTE_LIMITS
from map.map_parser import MapParser

logger = logging.getLogger(__name__)


class DataReceiverAgent:
    """校验输入数据完整性与合法性"""

    REQUIRED_FIELDS = [
        "obstacle_ratio", "map_width", "map_height",
        "connectivity", "topology_randomness", "compute_limit"
    ]

    OPTIONAL_FIELDS = ["start_point", "target_point", "dynamic_change_rate"]

    def validate(self, env: dict, map_filepath: str | None = None) -> dict:
        tasks: list = []
        if map_filepath is not None:
            try:
                parsed = MapParser().parse(map_filepath)
            except Exception as exc:
                logger.error("MapParser 解析失败 (%s): %s", map_filepath, exc, exc_info=True)
                raise ValueError(f"地图文件解析失败 ({map_filepath}): {exc}") from exc

            grid = parsed.get("grid")
            tasks = parsed.get("tasks") or []

            if "obstacle_ratio" not in env and grid is not None:
                env["obstacle_ratio"] = float(np.count_nonzero(grid == 1)) / grid.size
            if "map_width" not in env and grid is not None:
                env["map_width"] = int(grid.shape[1])
            if "map_height" not in env and grid is not None:
                env["map_height"] = int(grid.shape[0])

            if "start_point" not in env and tasks:
                t0 = tasks[0]
                env["start_point"] = [int(t0["start_x"] - 1), int(t0["start_y"] - 1)]
            if "target_point" not in env and tasks:
                t0 = tasks[0]
                env["target_point"] = [int(t0["target_x"] - 1), int(t0["target_y"] - 1)]

        required_fields = ["compute_limit"] if map_filepath is not None else self.REQUIRED_FIELDS
        for field in required_fields:
            if field not in env:
                raise ValueError(f"缺少必要字段: {field}")

        if not (0 <= env["obstacle_ratio"] <= 1):
            raise ValueError("obstacle_ratio 必须在 0 到 1 之间")
        if not (0 <= env.get("connectivity", 0) <= 1):
            raise ValueError("connectivity 必须在 0 到 1 之间")
        if not (0 <= env.get("topology_randomness", 0) <= 1):
            raise ValueError("topology_randomness 必须在 0 到 1 之间")
        if env["compute_limit"] not in COMPUTE_LIMITS:
            raise ValueError(f"compute_limit 必须为 {COMPUTE_LIMITS}")
        if env["map_width"] <= 0 or env["map_height"] <= 0:
            raise ValueError("地图尺寸必须大于 0")

        for point_field in ("start_point", "target_point"):
            if point_field in env:
                value = env[point_field]
                if not isinstance(value, (list, tuple)) or len(value) != 2:
                    raise ValueError(f"{point_field} 非法值: {value!r}")
                if not all(isinstance(item, int) and not isinstance(item, bool) for item in value):
                    raise ValueError(f"{point_field} 非法值: {value!r}")

        if "dynamic_change_rate" in env:
            rate = env["dynamic_change_rate"]
            if isinstance(rate, bool) or not isinstance(rate, (int, float)):
                raise ValueError(f"dynamic_change_rate 非法值: {rate!r}")
            if not (0 <= rate <= 1):
                raise ValueError(f"dynamic_change_rate 非法值: {rate!r}")

        env["input_validated"] = True
        env["validation_timestamp"] = (
            datetime.now(timezone.utc)
            .isoformat(timespec='seconds')
            .replace('+00:00', 'Z')
        )

        if map_filepath is not None:
            env["data_source"] = "benchmark" if tasks else "map_file"
        else:
            env["data_source"] = "manual_params"

        return env

    def validate_state(self, env_input: dict) -> "ResearchState":
        """Phase 4 入口：接收 ``env_input`` dict，校验后写入 ``ResearchState``。"""
        from agents.research_state import ResearchState  # 避免循环导入

        env = dict(env_input or {})
        try:
            validated = self.validate(env)
        except Exception as exc:
            logger.error("DataReceiverAgent.validate 失败: %s", exc, exc_info=True)
            # 即使校验失败也尽量构造 state，把错误记到 metadata
            rs = ResearchState(env_input=env)
            if rs.metadata is None:
                rs.metadata = {}
            rs.metadata.setdefault("errors", []).append(
                f"DataReceiverAgent.validate 失败: {exc}"
            )
            return rs

        rs = ResearchState(env_input=validated)
        if rs.metadata is None:
            rs.metadata = {}
        rs.metadata["validated"] = True
        rs.metadata.setdefault("errors", [])
        # 把 start_point / target_point 等可选字段也保留到 env_input
        return rs