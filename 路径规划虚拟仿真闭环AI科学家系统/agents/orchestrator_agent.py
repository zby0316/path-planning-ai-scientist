# agents/orchestrator_agent.py — 多智能体中央调度器（Phase 4：12+ 智能体）
"""基于 ``ResearchState`` 的 12+ 智能体全流水线调度器。

设计要点
--------
- ``__init__`` 实例化全部 14 个智能体（Phase 4 spec 要求）。
- ``run(env_input: dict) -> ResearchState`` 按 spec 顺序串联 12+ 个步骤。
- 每个步骤用 ``try/except`` 包裹，失败时把异常追加到
  ``state.metadata["errors"]`` 并继续执行，**不中断后续智能体**。
- 旧 ``OrchestratorAgent.run`` 的 dict 返回形态（"env"/"decision"/"explanation"/"hypothesis"）
  已被 ``main.py`` 中的 ``PathPlanningDecisionSystem`` 替代；本类专注于
  ``ResearchState`` 流水线。

向后兼容
--------
- ``OrchestratorAgent`` 仍然可被导入（``from agents.orchestrator_agent import
  OrchestratorAgent``），旧 ``run`` 接口已替换为返回 ``ResearchState``。
  ``main.py`` 不再使用 ``OrchestratorAgent``，改用 ``PathPlanningDecisionSystem``，
  因此 Phase 0/1 既有契约不被破坏。
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict

from agents.data_agent import DataReceiverAgent
from agents.decision_agent import DecisionAgent
from agents.environment_agent import EnvironmentAgent
from agents.evaluation_agent import AlgorithmEvaluationAgent
from agents.explanation_agent import ExplanationAgent
from agents.fact_extraction_agent import FactExtractionAgent
from agents.human_loop_agent import HumanLoopAgent
from agents.hypothesis_agent import HypothesisAgent
from agents.knowledge_agent import KnowledgeRetrievalAgent
from agents.literature_agent import LiteratureAgent
from agents.map_analysis_agent import MapAnalysisAgent
from agents.parameter_agent import ParameterAgent
from agents.reflection_agent import ReflectionAgent
from agents.research_state import ResearchState
from agents.rule_agent import RuleConstraintAgent

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """12+ 智能体中央调度器（Phase 4）。"""

    def __init__(self, use_qwen: bool = False) -> None:
        # 14 个智能体属性
        self.data_agent = DataReceiverAgent()
        self.map_agent = MapAnalysisAgent()
        self.env_agent = EnvironmentAgent()
        self.literature_agent = LiteratureAgent()
        self.fact_agent = FactExtractionAgent(use_qwen=use_qwen)
        self.knowledge_agent = KnowledgeRetrievalAgent()
        self.rule_agent = RuleConstraintAgent()
        self.eval_agent = AlgorithmEvaluationAgent()
        self.parameter_agent = ParameterAgent()
        self.decision_agent = DecisionAgent()
        self.human_agent = HumanLoopAgent()
        self.explanation_agent = ExplanationAgent(use_qwen=use_qwen)
        self.hypothesis_agent = HypothesisAgent(use_qwen=use_qwen)
        self.reflection_agent = ReflectionAgent(use_qwen=use_qwen)

    # ------------------------------------------------------------------ #
    # 主流程
    # ------------------------------------------------------------------ #
    def run(self, env_input: Dict[str, Any]) -> ResearchState:
        """12+ 智能体流水线，失败不中断。"""
        state = ResearchState(env_input=dict(env_input or {}))
        start_time = time.time()
        logger.info("流水线开始，env_input 关键字段: obstacle_ratio=%s, compute_limit=%s",
                    env_input.get("obstacle_ratio", "N/A"),
                    env_input.get("compute_limit", "N/A"))
        if state.metadata is None:
            state.metadata = {}
        state.metadata.setdefault("errors", [])

        state = self._safe_step(
            state,
            "DataReceiverAgent.validate_state",
            lambda: self.data_agent.validate_state(env_input or {}),
        )
        state = self._safe_step(
            state, "MapAnalysisAgent.analyze",
            lambda: self.map_agent.analyze(state),
        )
        state = self._safe_step(
            state, "EnvironmentAgent.classify_state",
            lambda: self.env_agent.classify_state(state),
        )
        state = self._safe_step(
            state, "LiteratureAgent.enrich_state",
            lambda: self.literature_agent.enrich_state(state),
        )
        state = self._safe_step(
            state, "FactExtractionAgent.enrich_state",
            lambda: self.fact_agent.enrich_state(state),
        )
        state = self._safe_step(
            state, "KnowledgeRetrievalAgent.retrieve_state",
            lambda: self.knowledge_agent.retrieve_state(state),
        )
        state = self._safe_step(
            state, "RuleConstraintAgent.filter_and_penalize_state",
            lambda: self.rule_agent.filter_and_penalize_state(state),
        )
        state = self._safe_step(
            state, "AlgorithmEvaluationAgent.score_state",
            lambda: self.eval_agent.score_state(state),
        )
        state = self._safe_step(
            state, "DecisionAgent.select_best_state",
            lambda: self.decision_agent.select_best_state(state),
        )
        state = self._safe_step(
            state, "HumanLoopAgent.check",
            lambda: self.human_agent.check(state),
        )
        state = self._safe_step(
            state, "ExplanationAgent.explain_state",
            lambda: self.explanation_agent.explain_state(state),
        )
        state = self._safe_step(
            state, "HypothesisAgent.generate_state",
            lambda: self.hypothesis_agent.generate_state(state),
        )
        state = self._safe_step(
            state, "ReflectionAgent.reflect",
            lambda: self.reflection_agent.reflect(state),
        )

        # 最后写入 recommended_params
        try:
            state.recommended_params = self.parameter_agent.recommend(
                state.env_input or {},
                state.decision or {},
            )
        except Exception as exc:
            state.metadata.setdefault("errors", []).append(
                f"ParameterAgent.recommend 失败: {exc}"
            )

        total_elapsed = time.time() - start_time
        logger.info("流水线完成，总耗时 %.3fs，state 摘要:\n%s", total_elapsed, state.summary())

        return state

    # ------------------------------------------------------------------ #
    def _safe_step(self, state: ResearchState, name: str, fn) -> ResearchState:
        """包装单个智能体步骤，失败时把错误追加到 ``state.metadata["errors"]``，返回原 state。"""
        step_start = time.time()
        logger.info("开始执行智能体步骤: %s", name)
        try:
            result = fn()
            elapsed = time.time() - step_start
            logger.info("智能体步骤完成: %s，耗时 %.3fs", name, elapsed)
            if result is None:
                return state
            return result
        except Exception as exc:
            logger.error("智能体步骤 %s 失败: %s", name, exc, exc_info=True)
            if state.metadata is None:
                state.metadata = {}
            state.metadata.setdefault("errors", []).append(f"{name} 失败: {exc}")
            return state


__all__ = ["OrchestratorAgent"]
