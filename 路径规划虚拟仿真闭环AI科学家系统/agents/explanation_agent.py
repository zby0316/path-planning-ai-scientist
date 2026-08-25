# agents/explanation_agent.py — 解释生成智能体

import logging

from llm.qwen_client import QwenClient
from llm.prompt_templates import (
    EXPLANATION_SYSTEM_PROMPT,
    EXPLANATION_USER_TEMPLATE,
)

logger = logging.getLogger(__name__)


class ExplanationAgent:
    """调用 Qwen 生成可解释的选型依据"""

    def __init__(self, use_qwen: bool = True):
        self.use_qwen = use_qwen
        if use_qwen:
            self.client = QwenClient()

    def explain(self, env: dict, decision: dict) -> dict:
        if self.use_qwen:
            return self._qwen_explain(env, decision)
        else:
            return self._rule_explain(env, decision)

    def _qwen_explain(self, env: dict, decision: dict) -> dict:
        ranking_detail = self._format_ranking(decision["ranking"])
        user_prompt = EXPLANATION_USER_TEMPLATE.format(
            scene_level=decision["scene_level"],
            best_algorithm=decision["best_algorithm"],
            best_score=decision["best_score"],
            ranking_detail=ranking_detail,
            obstacle_ratio=env.get("obstacle_ratio", "N/A"),
            map_width=env.get("map_width", "N/A"),
            map_height=env.get("map_height", "N/A"),
            connectivity=env.get("connectivity", "N/A"),
            topology_randomness=env.get("topology_randomness", "N/A"),
            compute_limit=env.get("compute_limit", "N/A"),
        )
        text = self.client.chat(EXPLANATION_SYSTEM_PROMPT, user_prompt)
        return {"explanation_text": text}

    def _rule_explain(self, env: dict, decision: dict) -> dict:
        """无 Qwen 时的规则化解释"""
        reason = (
            f"当前障碍物占比为 {env.get('obstacle_ratio', 0):.2f}，"
            f"按照规则判定为{decision['scene_level']}；"
            f"通道连通性为 {env.get('connectivity', 0):.2f}，"
            f"算力限制为 {env.get('compute_limit', 'N/A')}。"
            f"综合五种算法评分，{decision['best_algorithm']} 得分最高"
            f"（{decision['best_score']}），因此被选为最优算法。"
        )
        text = (
            f"当前场景等级：{decision['scene_level']}\n"
            f"选定最优算法名称：{decision['best_algorithm']}\n"
            f"简短选型依据：{reason}"
        )
        return {"explanation_text": text}

    def _format_ranking(self, ranking: list) -> str:
        lines = []
        for i, r in enumerate(ranking, 1):
            lines.append(
                f"{i}. {r['algorithm']}: 得分={r['score']:.4f}, "
                f"耗时={r['avg_time']}s, 成功率={r['success_rate']}, "
                f"惩罚={r.get('penalty', 0)}"
            )
        return "\n".join(lines)

    def explain_state(self, state) -> "ResearchState":
        """Phase 4 入口：基于 ``state`` 生成解释，写入 ``state.metadata["explanation"]``。"""
        from agents.research_state import ResearchState  # 避免循环导入

        decision = state.decision or {}
        env = state.env_input or {}
        if not decision:
            return state
        try:
            result = self.explain(env, decision)
        except Exception as exc:
            logger.error("ExplanationAgent.explain 失败: %s", exc, exc_info=True)
            if state.metadata is None:
                state.metadata = {}
            state.metadata.setdefault("errors", []).append(
                f"ExplanationAgent.explain 失败: {exc}"
            )
            result = {"explanation_text": ""}
        if state.metadata is None:
            state.metadata = {}
        state.metadata["explanation"] = result
        return state
