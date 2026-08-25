# agents/reflection_agent.py — 反思智能体
"""对决策结果进行质疑和可信度检查（Phase 4，提示词 4-5）。

设计要点
--------
- 默认走 LLM 路径（``use_qwen=True`` 且 ``qwen_client`` 提供时）；
- ``use_qwen=False`` 时走离线 ``_rule_reflect``，便于无 API 环境下测试。
- 输出统一为 ``{"confidence_score", "issues", "suggestions", "passed"}``。
- 反思结果同时写入 ``state.metadata["reflection"]`` 与 ``state.reflection``。
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional

from agents.research_state import ResearchState
from llm.prompt_templates import (
    REFLECTION_SYSTEM_PROMPT,
    REFLECTION_USER_TEMPLATE,
)

logger = logging.getLogger(__name__)

_DEFAULT_CONFIDENCE = 0.6
_MIN_CONFIDENCE = 0.4
_MIN_EXPERIMENTS_PER_ALGO = 3
_KNOWN_SCENE_LEVELS = {"低复杂度", "中复杂度", "高复杂度"}


def _strip_code_fence(text: str) -> str:
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text.strip()


def _safe_load_json(text: str) -> Optional[Dict[str, Any]]:
    cleaned = _strip_code_fence(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning("ReflectionAgent._safe_load_json 直接解析失败，尝试正则提取")
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            logger.warning("ReflectionAgent._safe_load_json JSON 解析失败: %s", exc)
            return None


class ReflectionAgent:
    """决策反思智能体（Phase 4）。"""

    def __init__(
        self,
        qwen_client: Optional[Any] = None,
        use_qwen: bool = True,
    ) -> None:
        self.use_qwen = use_qwen
        self.client: Optional[Any] = None
        if use_qwen:
            if qwen_client is not None:
                self.client = qwen_client
            else:
                try:
                    from llm.qwen_client import QwenClient  # 延迟导入

                    self.client = QwenClient()
                except Exception as exc:  # 离线时优雅降级
                    logger.warning(
                        "QwenClient 初始化失败（%s），自动降级为 _rule_reflect",
                        exc,
                    )
                    self.client = None
                    self.use_qwen = False

    # ------------------------------------------------------------------ #
    def reflect(self, state: ResearchState) -> ResearchState:
        """对决策进行 7 项反思检查，结果写入 ``state``。"""
        if self.use_qwen and self.client is not None:
            try:
                result = self._qwen_reflect(state)
            except Exception as exc:
                logger.warning("Qwen 反思失败（%s），改用 _rule_reflect", exc)
                result = self._rule_reflect(state)
        else:
            result = self._rule_reflect(state)

        # 写入 state（双写：metadata + 顶层 reflection 字段）
        if state.metadata is None:
            state.metadata = {}
        state.metadata["reflection"] = result
        state.reflection = result
        return state

    # ------------------------------------------------------------------ #
    def _qwen_reflect(self, state: ResearchState) -> Dict[str, Any]:
        decision = state.decision or {}
        records = state.algorithm_records or state.scored_algorithms or []
        records_text = "\n".join(
            f"- {r.get('algorithm', '?')}: score={r.get('score', 'N/A')}, "
            f"success_rate={r.get('success_rate', 'N/A')}, "
            f"avg_time={r.get('avg_time', 'N/A')}, "
            f"scene_level={r.get('scene_level', 'N/A')}"
            for r in records
        ) or "（无）"
        lit_text = "\n".join(
            f"- {f.get('fact', str(f))} (verified={f.get('verified', 'N/A')})"
            if isinstance(f, dict)
            else f"- {f}"
            for f in (state.literature_facts or [])
        ) or "（无）"
        exp_text = json.dumps(state.experiment_results or [], ensure_ascii=False)

        user_prompt = REFLECTION_USER_TEMPLATE.format(
            scene_level=decision.get("scene_level", "N/A"),
            best_algorithm=decision.get("best_algorithm", "N/A"),
            best_score=decision.get("best_score", "N/A"),
            records=records_text,
            literature_facts=lit_text,
            experiment_results=exp_text,
            state_summary=state.summary(),
        )
        raw = self.client.chat(REFLECTION_SYSTEM_PROMPT, user_prompt, temperature=0.2)
        parsed = _safe_load_json(raw) or {}
        return self._normalize_result(parsed)

    # ------------------------------------------------------------------ #
    def _rule_reflect(self, state: ResearchState) -> Dict[str, Any]:
        """离线规则反思：7 项硬规则检查。"""
        issues: List[str] = []
        suggestions: List[str] = []
        confidence = _DEFAULT_CONFIDENCE
        hard_fault = False

        decision = state.decision or {}
        records = state.algorithm_records or state.scored_algorithms or []
        literature_facts = state.literature_facts or []
        scene_level = decision.get("scene_level", "")
        best_algorithm = decision.get("best_algorithm", "")

        # 0. 知识库为空 → 硬伤
        if not records:
            issues.append("知识库为空（algorithm_records 为空），无法交叉验证推荐算法。")
            suggestions.append("补充历史实验数据或回退到 SQLite / JSON 知识库。")
            hard_fault = True
            confidence = min(confidence, _MIN_CONFIDENCE)

        # 1. 推荐算法是否真的是实验最优
        if records and best_algorithm:
            best_by_score = max(
                records,
                key=lambda r: float(r.get("score", 0) or 0),
                default=None,
            )
            if best_by_score and best_by_score.get("algorithm") != best_algorithm:
                issues.append(
                    f"推荐算法 '{best_algorithm}' 与按知识库得分最高算法 "
                    f"'{best_by_score.get('algorithm')}' 不一致。"
                )
                suggestions.append("复核评分函数权重或确认推荐算法是否经过规则惩罚调整。")
                confidence = min(confidence, 0.5)

        # 2. 是否存在另一个算法成功率更高
        if records:
            top_by_success = max(
                records,
                key=lambda r: float(r.get("success_rate", 0) or 0),
                default=None,
            )
            if (
                top_by_success
                and best_algorithm
                and top_by_success.get("algorithm") != best_algorithm
            ):
                top_rate = float(top_by_success.get("success_rate", 0))
                cur_rate = 0.0
                for r in records:
                    if r.get("algorithm") == best_algorithm:
                        cur_rate = float(r.get("success_rate", 0))
                        break
                if top_rate - cur_rate > 0.05:
                    issues.append(
                        f"算法 '{top_by_success.get('algorithm')}' 成功率 "
                        f"({top_rate:.2f}) 高于推荐算法 '{best_algorithm}' ({cur_rate:.2f})。"
                    )
                    suggestions.append("在高成功率优先场景下考虑切换为成功率最高的算法。")
                    confidence = min(confidence, 0.5)

        # 3. 是否只是耗时最短但成功率不足
        if records:
            fastest = min(
                records,
                key=lambda r: float(r.get("avg_time", float("inf")) or float("inf")),
                default=None,
            )
            if (
                fastest
                and best_algorithm == fastest.get("algorithm")
                and float(fastest.get("success_rate", 0)) < 0.7
            ):
                issues.append(
                    f"推荐算法仅耗时最短（{fastest.get('avg_time')}s）但成功率偏低 "
                    f"({fastest.get('success_rate')})。"
                )
                suggestions.append("在非时间优先场景下，应优先考虑成功率更高的算法。")
                confidence = min(confidence, 0.45)

        # 4. 文献依据真实性
        if not literature_facts:
            issues.append("当前决策无文献事实依据。")
            suggestions.append("补充 Semantic Scholar 文献检索或人工添加事实。")
            confidence = min(confidence, 0.45)
        else:
            unverified = [
                f for f in literature_facts
                if isinstance(f, dict) and f.get("verified") is False
            ]
            if unverified:
                issues.append(
                    f"引用文献中有 {len(unverified)} 条 verified == False，真实性存疑。"
                )
                suggestions.append("人工核查无法核验的文献条目。")
                confidence = min(confidence, 0.4)
                hard_fault = True

        # 5. 数据是否覆盖低/中/高复杂度
        present_levels = {r.get("scene_level") for r in records if r.get("scene_level")}
        missing = _KNOWN_SCENE_LEVELS - present_levels
        if missing and records:
            issues.append(
                f"知识库未覆盖以下场景等级: {sorted(missing)}，"
                f"可能导致跨等级泛化不可靠。"
            )
            suggestions.append("补充缺失场景等级的实验数据。")
            confidence = min(confidence, 0.5)

        # 6. 实验次数是否足够（≥3 次/算法）
        experiment_results = state.experiment_results or []
        if records and not experiment_results:
            issues.append(
                "暂无实验运行结果（experiment_results 为空），"
                f"按规范每个算法至少需要 {_MIN_EXPERIMENTS_PER_ALGO} 次重复实验。"
            )
            suggestions.append("运行 benchmark 并为每种算法累计 ≥ 3 次实验。")
            confidence = min(confidence, 0.45)
        elif experiment_results and records:
            counts: Dict[str, int] = {}
            for er in experiment_results:
                if not isinstance(er, dict):
                    continue
                algo = er.get("algorithm")
                if algo:
                    counts[algo] = counts.get(algo, 0) + 1
            insufficient = [
                a for a, c in counts.items() if c < _MIN_EXPERIMENTS_PER_ALGO
            ]
            if insufficient:
                issues.append(
                    f"以下算法实验次数不足 {_MIN_EXPERIMENTS_PER_ALGO}: {insufficient}。"
                )
                suggestions.append("补充实验以达到 ≥ 3 次/算法。")
                confidence = min(confidence, 0.5)

        # 7. 结论是否过度泛化
        if (
            best_algorithm
            and scene_level
            and not records
        ):
            issues.append(
                f"知识库缺失，无法验证 '{best_algorithm}' 在 '{scene_level}' "
                f"下的表现是否真的最优，结论可能过度泛化。"
            )
            suggestions.append("在补全数据前避免将该结论外推到其他场景。")
            confidence = min(confidence, 0.4)
            hard_fault = True

        passed = not hard_fault and confidence >= 0.5
        return self._normalize_result(
            {
                "confidence_score": round(confidence, 3),
                "issues": issues,
                "suggestions": suggestions,
                "passed": bool(passed),
            }
        )

    # ------------------------------------------------------------------ #
    @staticmethod
    def _normalize_result(parsed: Dict[str, Any]) -> Dict[str, Any]:
        """统一输出 schema，缺字段补默认。"""
        try:
            confidence = float(parsed.get("confidence_score", _DEFAULT_CONFIDENCE))
        except (TypeError, ValueError):
            confidence = _DEFAULT_CONFIDENCE
        confidence = max(0.0, min(1.0, confidence))

        def _to_list(v: Any) -> List[str]:
            if v is None:
                return []
            if isinstance(v, list):
                return [str(x) for x in v if x is not None]
            return [str(v)]

        issues = _to_list(parsed.get("issues"))
        suggestions = _to_list(parsed.get("suggestions"))
        passed = bool(parsed.get("passed", True))

        return {
            "confidence_score": round(confidence, 3),
            "issues": issues,
            "suggestions": suggestions,
            "passed": passed,
        }


__all__ = ["ReflectionAgent"]
