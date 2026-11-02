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

    # ------------------------------------------------------------------ #
    def run_full_cycle(
        self, env_input: Dict[str, Any], max_iterations: int = 3
    ) -> ResearchState:
        """完整流水线：orchestrator → 迭代(hypothesis → experiment → reflection)。"""
        from agents.application_service import ApplicationService
        result = ApplicationService().run_cycle(env_input, max_iterations=max_iterations)
        state = ResearchState(env_input=result["env_input"])
        state.algorithm_records = result["prior_ranking"]
        state.scored_algorithms = result["decision"]["ranking"]
        state.decision = result["decision"]
        state.hypothesis = result["hypothesis"]
        state.experiment_results = result["experiment_results"]
        state.reflection = result["reflection"]
        state.report = result["report"]
        state.metadata.update({
            "status": result["status"], "cycle_id": result["cycle_id"],
            "iterations": result["iterations"], "hypothesis_supported": result["hypothesis_supported"],
            "degraded": result["degraded"], "timings": result["timings"],
        })
        if self.use_qwen:
            state.metadata["degraded"].append("统一核心流程离线运行，未调用 Qwen")
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
        if state.report:
            with open(filepath, 'w', encoding='utf-8') as output:
                output.write(state.report)
            return os.path.abspath(filepath)
        return ReportGenerator(state).save_to_file(filepath=filepath)
