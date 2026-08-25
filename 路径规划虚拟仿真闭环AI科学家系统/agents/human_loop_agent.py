# agents/human_loop_agent.py — 人在回路智能体
"""检测异常情况，触发人工校验提示（Phase 4 升级至 7 条件）。

设计要点
--------
- **不破坏** Phase 0/1 既有 ``check(decision: dict) -> dict`` 接口；
  旧调用方（仅 1 条件：前两名得分差）行为保持不变。
- 新增 ``check_state(state: ResearchState) -> ResearchState``，按 7 条件判定。
- ``check`` 现在是"薄包装"：识别到 ``ResearchState`` 时委托到 ``check_state``，
  否则走旧路径（仅 1 条件）。
- 所有命中原因（中文）追加到 ``state.metadata["human_check_reasons"]``；
  列表非空时同步 ``state.decision["need_human_check"] = True``。
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from config import SCORE_GAP_THRESHOLD

logger = logging.getLogger(__name__)

# 用户权重偏好（条件 5）
_VALID_USER_PREFERENCES = {"safety_first", "time_first", "success_first"}

# 条件 4：高复杂度 + 全部算法成功率 < 该阈值
_LOW_SUCCESS_RATE_THRESHOLD = 0.5


class HumanLoopAgent:
    """人在回路智能体（Phase 4：7 条件）。"""

    def __init__(self) -> None:
        # 兼容旧字段（条件 1）
        self.score_gap_threshold = SCORE_GAP_THRESHOLD

    # ------------------------------------------------------------------ #
    # 旧接口（Phase 0/1）：1 条件，接收 dict，返回 dict
    # ------------------------------------------------------------------ #
    def check(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """薄包装：识别到 ``ResearchState`` 时委托到 ``check_state``。

        Parameters
        ----------
        decision : dict
            - Phase 0/1 调用方：传入 ``decision`` 字典（含 ``ranking``），原地
              设置 ``need_human_check`` / ``human_check_reason`` 后返回；
            - Phase 4 调用方：传入 ``ResearchState`` 实例，委托 ``check_state``。
        """
        from agents.research_state import ResearchState  # 避免循环导入

        if isinstance(decision, ResearchState):
            return self.check_state(decision)

        # 旧 1 条件：前两名得分差 < SCORE_GAP_THRESHOLD
        ranking = (decision or {}).get("ranking") or []
        if len(ranking) >= 2:
            gap = ranking[0]["score"] - ranking[1]["score"]
            if gap < self.score_gap_threshold:
                decision["need_human_check"] = True
                decision["human_check_reason"] = (
                    f"前两名算法（{ranking[0]['algorithm']} 与 {ranking[1]['algorithm']}）"
                    f"评分差距仅 {gap:.4f}，小于阈值 {self.score_gap_threshold}，"
                    f"建议人工确认优化优先级。"
                )
            else:
                decision["need_human_check"] = False
        return decision

    # ------------------------------------------------------------------ #
    # 新接口（Phase 4）：7 条件，接收 ResearchState，返回 ResearchState
    # ------------------------------------------------------------------ #
    def check_state(self, state) -> "ResearchState":
        """按 7 种触发条件判定 ``need_human_check``，结果写入 ``state``。"""
        from agents.research_state import ResearchState  # 避免循环导入

        if state.metadata is None:
            state.metadata = {}
        state.metadata.setdefault("human_check_reasons", [])
        reasons: List[str] = state.metadata["human_check_reasons"]

        # 确保 decision 字典存在
        if state.decision is None:
            state.decision = {}

        for reason in self._evaluate(state):
            if reason and reason not in reasons:
                reasons.append(reason)

        if reasons:
            state.decision["need_human_check"] = True
        else:
            state.decision.setdefault("need_human_check", False)

        return state

    # ------------------------------------------------------------------ #
    # 7 条件核心
    # ------------------------------------------------------------------ #
    def _evaluate(self, state) -> List[str]:
        reasons: List[str] = []

        decision = state.decision or {}
        algorithm_records: List[Dict[str, Any]] = list(state.algorithm_records or [])
        scored_algorithms: List[Dict[str, Any]] = list(state.scored_algorithms or [])
        env_input: Dict[str, Any] = state.env_input or {}
        scene_level = (
            decision.get("scene_level")
            or (state.metadata or {}).get("scene_level")
            or ""
        )
        best_algorithm = decision.get("best_algorithm", "")

        # 条件 1：前两名得分差 < SCORE_GAP_THRESHOLD
        ranking_src = decision.get("ranking") or scored_algorithms
        if len(ranking_src) >= 2:
            try:
                gap = float(ranking_src[0].get("score", 0)) - float(
                    ranking_src[1].get("score", 0)
                )
            except (TypeError, ValueError) as exc:
                logger.warning("HumanLoopAgent 得分差计算失败: %s", exc)
                gap = float("inf")
            if gap < self.score_gap_threshold:
                reasons.append(
                    f"前两名算法（{ranking_src[0].get('algorithm', '?')} 与 "
                    f"{ranking_src[1].get('algorithm', '?')}）评分差距仅 {gap:.4f}，"
                    f"小于阈值 {self.score_gap_threshold}，建议人工确认优化优先级。"
                )

        # 条件 2：知识库中场景等级无记录（algorithm_records 为空 / 与 scene_level 不匹配）
        if not algorithm_records:
            reasons.append(
                f"知识库中未检索到场景等级 '{scene_level or '未知'}' 的算法历史记录，"
                f"评分依据不充分。"
            )
        else:
            matched = [r for r in algorithm_records if r.get("scene_level") == scene_level]
            if scene_level and not matched:
                reasons.append(
                    f"知识库中未命中场景等级 '{scene_level}'，当前决策依据来自其他等级的数据。"
                )

        # 条件 3：推荐算法与"成功率/得分最高者"不一致
        if best_algorithm and algorithm_records:
            best_by_score = max(
                algorithm_records,
                key=lambda r: float(r.get("score", r.get("success_rate", 0)) or 0),
                default=None,
            )
            if (
                best_by_score
                and best_by_score.get("algorithm") != best_algorithm
            ):
                gap_to_best = 0.0
                if ranking_src and ranking_src[0].get("algorithm") == best_algorithm:
                    try:
                        gap_to_best = (
                            float(best_by_score.get("score", 0))
                            - float(ranking_src[0].get("score", 0))
                        )
                    except (TypeError, ValueError) as exc:
                        logger.warning("HumanLoopAgent 计算 gap_to_best 失败: %s", exc)
                        gap_to_best = 0.0
                if gap_to_best > 0.05:
                    reasons.append(
                        f"推荐算法 '{best_algorithm}' 与按知识库得分最高算法 "
                        f"'{best_by_score.get('algorithm')}' 不一致（差距 {gap_to_best:.4f}）。"
                    )

        # 条件 4：高复杂度 + 全部算法 success_rate < 0.5
        if scene_level == "高复杂度" and algorithm_records:
            rates = [
                float(r.get("success_rate", 0) or 0)
                for r in algorithm_records
            ]
            if rates and max(rates) < _LOW_SUCCESS_RATE_THRESHOLD:
                reasons.append(
                    f"高复杂度场景下所有算法成功率均 < {_LOW_SUCCESS_RATE_THRESHOLD}，"
                    f"无可靠解，建议人工干预或调低地图复杂度。"
                )

        # 条件 5：用户权重偏好
        user_pref = env_input.get("user_preference")
        if isinstance(user_pref, str) and user_pref in _VALID_USER_PREFERENCES:
            reasons.append(
                f"用户已指定权重偏好 '{user_pref}'，建议人工确认选型是否与偏好一致。"
            )

        # 条件 6：文献事实 < 2 条
        lit_facts = list(state.literature_facts or [])
        if len(lit_facts) < 2:
            reasons.append(
                f"当前决策可引用的文献事实不足（{len(lit_facts)} 条 < 2 条），"
                f"建议补充文献或人工核查。"
            )

        # 条件 7：引用的文献中存在 verified == False
        unverified = [
            f for f in lit_facts
            if isinstance(f, dict) and f.get("verified") is False
        ]
        if unverified:
            reasons.append(
                f"引用文献中有 {len(unverified)} 条无法核验（verified == False），"
                f"建议人工核查引用真实性。"
            )

        return reasons


__all__ = ["HumanLoopAgent"]
