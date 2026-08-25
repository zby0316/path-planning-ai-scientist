"""多智能体模块（Phase 5：在 Phase 4 基础上导出 ``ResearchState`` / ``MapAnalysisAgent`` /
``ReflectionAgent`` 等新增类，同时保留对历史智能体的导出）。

使用方式
--------
``from agents import ResearchState, MapAnalysisAgent, OrchestratorAgent, ...``
"""

from agents.citation_agent import CitationAgent  # noqa: F401
from agents.data_agent import DataReceiverAgent  # noqa: F401
from agents.decision_agent import DecisionAgent  # noqa: F401
from agents.environment_agent import EnvironmentAgent  # noqa: F401
from agents.evaluation_agent import AlgorithmEvaluationAgent  # noqa: F401
from agents.explanation_agent import ExplanationAgent  # noqa: F401
from agents.experiment_agent import ExperimentAgent  # noqa: F401  (Phase 5)
from agents.fact_extraction_agent import FactExtractionAgent  # noqa: F401
from agents.human_loop_agent import HumanLoopAgent  # noqa: F401
from agents.hypothesis_agent import HypothesisAgent  # noqa: F401
from agents.knowledge_agent import KnowledgeRetrievalAgent  # noqa: F401
from agents.literature_agent import LiteratureAgent  # noqa: F401
from agents.map_analysis_agent import MapAnalysisAgent  # noqa: F401  (Phase 4)
from agents.orchestrator_agent import OrchestratorAgent  # noqa: F401
from agents.parameter_agent import ParameterAgent  # noqa: F401
from agents.pipeline import ScientificDiscoveryPipeline  # noqa: F401  (Phase 5)
from agents.rag_agent import RAGAgent  # noqa: F401
from agents.reflection_agent import ReflectionAgent  # noqa: F401  (Phase 4)
from agents.research_state import ResearchState  # noqa: F401  (Phase 4)
from agents.rule_agent import RuleConstraintAgent  # noqa: F401

__all__ = [
    "AlgorithmEvaluationAgent",
    "CitationAgent",
    "DataReceiverAgent",
    "DecisionAgent",
    "EnvironmentAgent",
    "ExplanationAgent",
    "ExperimentAgent",
    "FactExtractionAgent",
    "HumanLoopAgent",
    "HypothesisAgent",
    "KnowledgeRetrievalAgent",
    "LiteratureAgent",
    "MapAnalysisAgent",
    "OrchestratorAgent",
    "ParameterAgent",
    "RAGAgent",
    "ReflectionAgent",
    "ResearchState",
    "RuleConstraintAgent",
    "ScientificDiscoveryPipeline",
]
