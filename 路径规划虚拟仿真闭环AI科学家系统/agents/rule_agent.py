# agents/rule_agent.py — 规则约束智能体

import logging

from config import (
    PENALTY_HIGH_TIME_THRESHOLD, PENALTY_HIGH_TIME_VALUE,
    PENALTY_LOW_SUCCESS_RATE, PENALTY_LOW_SUCCESS_VALUE,
    PENALTY_OVERKILL_VALUE, PENALTY_POOR_CONNECTIVITY_SUCCESS,
    PENALTY_POOR_CONNECTIVITY_VALUE, POOR_CONNECTIVITY_THRESHOLD,
)

logger = logging.getLogger(__name__)


class RuleConstraintAgent:
    """根据硬性规则对候选算法施加惩罚项"""

    def filter_and_penalize(self, env: dict, records: list) -> list:
        processed = []
        for record in records:
            penalty = 0.0
            algorithm = record["algorithm"]

            # 规则1：算力受限时惩罚高耗时算法
            if env["compute_limit"] == "low" and record["avg_time"] > PENALTY_HIGH_TIME_THRESHOLD:
                penalty += PENALTY_HIGH_TIME_VALUE

            # 规则2：高复杂度场景惩罚低成功率算法
            if env["scene_level"] == "高复杂度" and record["success_rate"] < PENALTY_LOW_SUCCESS_RATE:
                penalty += PENALTY_LOW_SUCCESS_VALUE

            # 规则3：低复杂度场景中使用过度复杂算法轻微惩罚
            if env["scene_level"] == "低复杂度" and algorithm == "混合优化算法":
                penalty += PENALTY_OVERKILL_VALUE

            # 规则4：连通性差时惩罚成功率较低算法
            if env.get("connectivity", 1.0) < POOR_CONNECTIVITY_THRESHOLD and \
               record["success_rate"] < PENALTY_POOR_CONNECTIVITY_SUCCESS:
                penalty += PENALTY_POOR_CONNECTIVITY_VALUE

            record = record.copy()
            record["penalty"] = penalty
            processed.append(record)

        return processed

    def filter_and_penalize_state(self, state) -> "ResearchState":
        """Phase 4 入口：从 ``state.algorithm_records`` + ``state.env_input`` 计算惩罚。"""
        from agents.research_state import ResearchState  # 避免循环导入

        records = list(state.algorithm_records or [])
        env = dict(state.env_input or {})
        if "scene_level" not in env and state.metadata is not None:
            env["scene_level"] = state.metadata.get("scene_level", "未知")
        try:
            processed = self.filter_and_penalize(env, records)
        except Exception as exc:
            logger.error("RuleConstraintAgent.filter_and_penalize 失败: %s", exc, exc_info=True)
            if state.metadata is None:
                state.metadata = {}
            state.metadata.setdefault("errors", []).append(
                f"RuleConstraintAgent.filter_and_penalize 失败: {exc}"
            )
            processed = records
        state.algorithm_records = processed
        return state
