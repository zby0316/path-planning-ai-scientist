# agents/decision_agent.py — 决策生成智能体

import logging

from config import ALLOWED_ALGORITHMS

logger = logging.getLogger(__name__)


class DecisionAgent:
    """选择得分最高的算法，生成标准化决策结果"""

    def select_best(self, env: dict, scored_records: list) -> dict:
        if not scored_records:
            raise ValueError("没有可用算法候选，请检查知识库数据")

        best = scored_records[0]

        if best["algorithm"] not in ALLOWED_ALGORITHMS:
            raise ValueError(f"非法算法 '{best['algorithm']}'，只允许从 {ALLOWED_ALGORITHMS} 中选择")

        return {
            "scene_level": env["scene_level"],
            "best_algorithm": best["algorithm"],
            "best_score": best["score"],
            "ranking": scored_records,
        }

    def select_best_state(self, state) -> "ResearchState":
        """Phase 4 入口：基于 ``state.scored_algorithms`` 选最优，写入 ``state.decision``。"""
        from agents.research_state import ResearchState  # 避免循环导入

        env = dict(state.env_input or {})
        if "scene_level" not in env and state.metadata is not None:
            env["scene_level"] = state.metadata.get("scene_level", "未知")
        scored = list(state.scored_algorithms or state.algorithm_records or [])
        try:
            decision = self.select_best(env, scored)
        except Exception as exc:
            logger.error("DecisionAgent.select_best 失败: %s", exc, exc_info=True)
            if state.metadata is None:
                state.metadata = {}
            state.metadata.setdefault("errors", []).append(
                f"DecisionAgent.select_best 失败: {exc}"
            )
            decision = {
                "scene_level": env.get("scene_level", "未知"),
                "best_algorithm": "",
                "best_score": 0.0,
                "ranking": scored,
            }
        state.decision = decision
        return state
