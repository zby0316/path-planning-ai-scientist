# agents/rag_agent.py — 检索增强生成智能体（RAG）

import logging
from typing import Any, Dict, List, Optional

from agents.fact_extraction_agent import FactExtractionAgent
from agents.literature_agent import LiteratureAgent
from data.experiment_db import ExperimentDB

logger = logging.getLogger(__name__)


def _safe_avg(values: List[float]) -> float:
    clean = [v for v in values if isinstance(v, (int, float))]
    if not clean:
        return 0.0
    return round(sum(clean) / len(clean), 4)


class RAGAgent:
    """RAG 智能体：整合文献事实与历史实验数据，为下游决策提供上下文。

    Parameters
    ----------
    literature_agent : LiteratureAgent
        已初始化的文献检索智能体。
    fact_extraction_agent : Optional[FactExtractionAgent]
        已初始化的事实抽取智能体；为 ``None`` 时仅返回文献事实。
    experiment_db : Optional[ExperimentDB]
        已初始化的实验数据库；为 ``None`` 时仅返回文献事实。
    """

    def __init__(
        self,
        literature_agent: Optional[LiteratureAgent] = None,
        fact_extraction_agent: Optional[FactExtractionAgent] = None,
        experiment_db: Optional[ExperimentDB] = None,
    ):
        self.literature_agent = literature_agent or LiteratureAgent()
        self.fact_extraction_agent = fact_extraction_agent
        self.experiment_db = experiment_db

    def _scene_obstacle_range(self, scene_level: str) -> tuple:
        return {
            "低复杂度": (0.0, 0.20),
            "中复杂度": (0.20, 0.50),
            "高复杂度": (0.50, 1.0),
        }.get(scene_level, (0.0, 1.0))

    def _query_historical_performance(self, scene_level: str,
                                      algorithm: str) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "source": "none",
            "algorithm": algorithm,
            "scene_level": scene_level,
            "n_runs": 0,
            "avg_runtime": 0.0,
            "avg_path_length": 0.0,
            "success_rate": 0.0,
        }
        if self.experiment_db is None:
            return result

        try:
            min_o, max_o = self._scene_obstacle_range(scene_level)
            runs = self.experiment_db.query_runs_by_scene(min_o, max_o)
        except Exception as exc:
            logger.error("RAGAgent._query_historical_performance 查询失败: %s", exc, exc_info=True)
            runs = []

        runs = [r for r in runs if r.get("algorithm") == algorithm]
        if not runs:
            return result

        return {
            "source": "sqlite",
            "algorithm": algorithm,
            "scene_level": scene_level,
            "n_runs": len(runs),
            "avg_runtime": _safe_avg([r.get("runtime", 0.0) for r in runs]),
            "avg_path_length": _safe_avg([r.get("path_length", 0.0) for r in runs]),
            "success_rate": _safe_avg(
                [float(r.get("success", 0)) for r in runs]
            ),
        }

    def _query_relevant_papers(self, algorithm: str) -> List[Dict[str, Any]]:
        keywords = [algorithm, "path planning"]
        matched = self.literature_agent.search_local(keywords)
        return [
            {
                "paper_id": p.paper_id,
                "title": p.title,
                "authors": p.authors,
                "year": p.year,
                "venue": p.venue,
                "doi": p.doi,
                "evidence_level": p.evidence_level,
            }
            for p in matched
        ]

    def retrieve(self, scene_level: str, algorithm: str) -> Dict[str, Any]:
        """检索与场景 + 算法相关的全部上下文。

        返回结构::
            {
                "scene_level": ...,
                "algorithm": ...,
                "literature_facts": [...],
                "historical_performance": {...},
                "relevant_papers": [...],
            }
        """
        literature_facts = self.literature_agent.get_paper_facts(algorithm)
        historical_performance = self._query_historical_performance(
            scene_level, algorithm
        )
        relevant_papers = self._query_relevant_papers(algorithm)

        return {
            "scene_level": scene_level,
            "algorithm": algorithm,
            "literature_facts": literature_facts,
            "historical_performance": historical_performance,
            "relevant_papers": relevant_papers,
        }
