# agents/pipeline.py — 假设-验证-反思闭环流水线（Phase 5，提示词 5-3）
"""整合 OrchestratorAgent → HypothesisAgent → ExperimentAgent → ReflectionAgent 形成闭环。"""
from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from agents.experiment_agent import ExperimentAgent
from agents.hypothesis_agent import HypothesisAgent
from agents.orchestrator_agent import OrchestratorAgent
from agents.reflection_agent import ReflectionAgent
from agents.research_state import ResearchState
from config import REPORTS_DIR
from data.experiment_db import ExperimentDB
from evaluation.benchmark import BenchmarkRunner

logger = logging.getLogger(__name__)

__all__ = ["ScientificDiscoveryPipeline"]

_CONFIDENCE_THRESHOLD = 0.7  # 反思 confidence_score >= 0.7 视为收敛


def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


class ScientificDiscoveryPipeline:
    """假设-验证-反思闭环（Phase 5，提示词 5-3）。"""

    def __init__(self, use_qwen: bool = False) -> None:
        self.use_qwen = use_qwen
        self.orchestrator = OrchestratorAgent(use_qwen=use_qwen)
        self.hypothesis_agent = HypothesisAgent(use_qwen=use_qwen)
        self.reflection_agent = ReflectionAgent(use_qwen=use_qwen)
        self.db = ExperimentDB()
        self.benchmark_runner = BenchmarkRunner()
        self.experiment_agent = ExperimentAgent(
            db=self.db, benchmark_runner=self.benchmark_runner
        )

    # ------------------------------------------------------------------ #
    def run_full_cycle(
        self, env_input: Dict[str, Any], max_iterations: int = 3
    ) -> ResearchState:
        """完整流水线：orchestrator → 迭代(hypothesis → experiment → reflection)。"""
        state = self.orchestrator.run(env_input)
        if state.metadata is None:
            state.metadata = {}
        state.metadata.setdefault("errors", [])
        state.metadata.setdefault("iterations", [])
        state.metadata.setdefault("hypothesis_revisions", [])

        if max_iterations <= 0:
            return state

        for iteration in range(1, max_iterations + 1):
            # a. 生成假设
            try:
                state = self.hypothesis_agent.generate(state)
            except Exception as exc:
                state.metadata["errors"].append(
                    f"iteration {iteration} HypothesisAgent.generate 失败: {exc}"
                )
            # b. 跑实验
            try:
                state = self.experiment_agent.run_validation(state)
            except Exception as exc:
                state.metadata["errors"].append(
                    f"iteration {iteration} ExperimentAgent.run_validation 失败: {exc}"
                )
            # c. 反思
            try:
                state = self.reflection_agent.reflect(state)
            except Exception as exc:
                state.metadata["errors"].append(
                    f"iteration {iteration} ReflectionAgent.reflect 失败: {exc}"
                )

            # d. 记录本轮结果
            hyp = state.hypothesis or {}
            reflection = state.reflection or {}
            iteration_record = {
                "iteration": iteration,
                "hypothesis_summary": hyp.get("hypothesis_text", "")[:200],
                "hypothesis_supported": state.metadata.get("hypothesis_supported"),
                "confidence_score": float(reflection.get("confidence_score", 0) or 0),
                "issues": list(reflection.get("issues", []) or []),
                "suggestions": list(reflection.get("suggestions", []) or []),
                "experiment_results_count": len(state.experiment_results or []),
            }
            state.metadata["iterations"].append(iteration_record)

            # e. 退出条件
            if iteration_record["confidence_score"] >= _CONFIDENCE_THRESHOLD:
                logger.info(
                    "iteration %d 达到 confidence_score=%.3f，提前收敛",
                    iteration,
                    iteration_record["confidence_score"],
                )
                break
            if iteration >= max_iterations:
                break
            # 未收敛 → 注入修正方向到下一轮
            state.metadata["hypothesis_revisions"].append({
                "iteration": iteration,
                "issues": list(reflection.get("issues", []) or []),
                "suggestions": list(reflection.get("suggestions", []) or []),
            })
            if state.decision is None:
                state.decision = {}
            state.decision.setdefault("revision_directions", []).append({
                "iteration": iteration,
                "issues": list(reflection.get("issues", []) or []),
            })

        return state

    # ------------------------------------------------------------------ #
    def export_report(
        self, state: ResearchState, filepath: Optional[str] = None
    ) -> str:
        """导出最终结果为 Markdown 报告。"""
        # 延迟导入以避免 reports → agents.pipeline → reports 的循环导入
        from reports.report_generator import ReportGenerator

        if filepath is None or os.path.isdir(filepath or ""):
            base_dir = filepath if (filepath and os.path.isdir(filepath)) else REPORTS_DIR
            os.makedirs(base_dir, exist_ok=True)
            ts = _now_iso().replace(":", "-")
            filepath = os.path.join(base_dir, f"report_{ts}.md")
        else:
            os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        generator = ReportGenerator(state)
        return generator.save_to_file(filepath=filepath)
