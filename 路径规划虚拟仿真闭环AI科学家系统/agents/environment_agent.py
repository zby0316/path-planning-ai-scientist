# agents/environment_agent.py — 环境复杂度分析智能体

import logging

from config import OBSTACLE_LOW_THRESHOLD, OBSTACLE_MEDIUM_THRESHOLD

logger = logging.getLogger(__name__)


class EnvironmentAgent:
    """将地图特征分为低/中/高三个复杂度等级"""

    def classify(self, env: dict) -> dict:
        obstacle_ratio = env["obstacle_ratio"]

        if obstacle_ratio < OBSTACLE_LOW_THRESHOLD:
            scene_level = "低复杂度"
        elif obstacle_ratio <= OBSTACLE_MEDIUM_THRESHOLD:
            scene_level = "中复杂度"
        else:
            scene_level = "高复杂度"

        complexity_index = (
            0.45 * obstacle_ratio +
            0.25 * (1 - env.get("connectivity", 0)) +
            0.20 * env.get("topology_randomness", 0) +
            0.10 * env.get("dynamic_change_rate", 0)
        )

        env["scene_level"] = scene_level
        env["complexity_index"] = round(complexity_index, 4)
        return env

    def classify_state(self, state) -> "ResearchState":
        """Phase 4 入口：基于 ``state.env_input`` 计算场景等级并写回 ``state``。"""
        from agents.research_state import ResearchState  # 避免循环导入

        if state.env_input is None or "obstacle_ratio" not in state.env_input:
            return state
        try:
            env = self.classify(dict(state.env_input))
        except Exception as exc:
            logger.error("EnvironmentAgent.classify 失败: %s", exc, exc_info=True)
            if state.metadata is None:
                state.metadata = {}
            state.metadata.setdefault("errors", []).append(
                f"EnvironmentAgent.classify 失败: {exc}"
            )
            return state
        state.env_input = env
        # 同步 scene_level 到 metadata，便于下游 HumanLoopAgent 读取
        if state.metadata is None:
            state.metadata = {}
        state.metadata["scene_level"] = env.get("scene_level", "未知")
        # 同步到 decision 字典（如已存在）
        if state.decision is not None:
            state.decision["scene_level"] = env.get("scene_level", "未知")
        return state
