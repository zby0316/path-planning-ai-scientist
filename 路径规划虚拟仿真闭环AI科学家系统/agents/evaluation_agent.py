# agents/evaluation_agent.py — 算法评估智能体（10 维评分）

import logging

from config import (
    WEIGHTS,
    COMPUTE_LIMIT_WEIGHT_ADJUST,
    NORMALIZATION_DIRECTION,
    SCORING_METRIC_KEYS,
)
from evaluation.scoring import (
    compute_score_detail,
    load_range_dict,
    _record_metric_range,
)

logger = logging.getLogger(__name__)


class AlgorithmEvaluationAgent:
    """归一化 + 加权评分，输出排序后的算法列表（10 维）"""

    def get_weights(self, env: dict) -> dict:
        weights = WEIGHTS[env["scene_level"]].copy()
        if env.get("compute_limit") == "low":
            for key, adj in COMPUTE_LIMIT_WEIGHT_ADJUST.items():
                weights[key] = weights.get(key, 0) + adj
        return weights

    def _normalize_reverse(self, value: float, min_value: float, max_value: float) -> float:
        if max_value == min_value:
            return 1.0
        score = 1.0 - (value - min_value) / (max_value - min_value)
        return float(max(0.0, min(1.0, score)))

    def _normalize_forward(self, value: float, min_value: float, max_value: float) -> float:
        if max_value == min_value:
            return 1.0
        score = (value - min_value) / (max_value - min_value)
        return float(max(0.0, min(1.0, score)))

    def score(self, env: dict, records: list) -> list:
        """对所有记录按 10 维指标计算加权综合得分"""
        weights = self.get_weights(env)

        # 归一化区间：优先预定义基准集（跨场景可比），缺失时回退当批 min/max
        range_dict, norm_source = load_range_dict(
            env.get("scene_level", ""), records=records,
        )
        if norm_source != "baseline":
            range_dict = {}
            for metric in SCORING_METRIC_KEYS:
                range_dict[metric] = _record_metric_range(records, metric)

        scored = []
        for record in records:
            detail = compute_score_detail(record, weights, range_dict)
            new_record = record.copy()
            new_record["score"] = detail["final_score"]
            new_record["detail"] = detail
            new_record["normalization_source"] = norm_source
            scored.append(new_record)

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def score_state(self, state) -> "ResearchState":
        """Phase 4 入口：对 ``state.algorithm_records`` 评分，结果写入 ``state.scored_algorithms``。"""
        from agents.research_state import ResearchState  # 避免循环导入

        records = list(state.algorithm_records or [])
        env = dict(state.env_input or {})
        if "scene_level" not in env and state.metadata is not None:
            env["scene_level"] = state.metadata.get("scene_level", "未知")
        try:
            scored = self.score(env, records)
        except Exception as exc:
            logger.error("AlgorithmEvaluationAgent.score 失败: %s", exc, exc_info=True)
            if state.metadata is None:
                state.metadata = {}
            state.metadata.setdefault("errors", []).append(
                f"AlgorithmEvaluationAgent.score 失败: {exc}"
            )
            scored = records
        state.scored_algorithms = scored
        return state
