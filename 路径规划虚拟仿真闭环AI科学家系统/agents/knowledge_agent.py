# agents/knowledge_agent.py — 知识库检索智能体

import json
import logging
from typing import List, Optional

from config import HISTORICAL_RESULTS_PATH, ALLOWED_ALGORITHMS
from data.experiment_db import ExperimentDB

logger = logging.getLogger(__name__)


def _scene_obstacle_range(scene_level: str) -> tuple:
    return {
        "低复杂度": (0.0, 0.20),
        "中复杂度": (0.20, 0.50),
        "高复杂度": (0.50, 1.0),
    }.get(scene_level, (0.0, 1.0))


class KnowledgeRetrievalAgent:
    """从历史性能数据库中检索匹配场景等级的算法记录。

    检索优先级：
    1. 当传入 ``experiment_db`` 时，优先从 SQLite 中按场景等级对应的
       障碍物比例区间查询 ``algorithm_runs`` 聚合后的算法记录。
    2. 若 SQLite 无数据，回退到 ``knowledge_base/historical_results.json``。
    """

    def __init__(self, experiment_db: Optional[ExperimentDB] = None):
        self.experiment_db = experiment_db

        try:
            with open(HISTORICAL_RESULTS_PATH, "r", encoding="utf-8") as f:
                self.performance_db = json.load(f)
        except FileNotFoundError:
            logger.warning(
                "未找到 %s，历史结果集为空", HISTORICAL_RESULTS_PATH
            )
            self.performance_db = []

    def _records_from_sqlite(self, scene_level: str) -> List[dict]:
        if self.experiment_db is None:
            return []

        min_o, max_o = _scene_obstacle_range(scene_level)
        try:
            runs = self.experiment_db.query_runs_by_scene(min_o, max_o)
        except Exception as exc:
            logger.warning("SQLite 查询失败，回退到 JSON: %s", exc)
            return []

        runs = [r for r in runs if r.get("algorithm") in ALLOWED_ALGORITHMS]
        if not runs:
            return []

        by_algo: dict = {}
        for r in runs:
            algo = r.get("algorithm", "unknown")
            by_algo.setdefault(algo, []).append(r)

        records: List[dict] = []
        for algo, items in by_algo.items():
            runtimes = [float(it.get("runtime", 0.0)) for it in items]
            lengths = [float(it.get("path_length", 0.0)) for it in items]
            successes = [float(bool(it.get("success", 0))) for it in items]
            stab = [float(it.get("stability_score", 0.0)) for it in items]
            smooth = [float(it.get("smoothness", 0.0) or 0.0) for it in items]
            safety = [float(it.get("safety_score", 0.0) or 0.0) for it in items]
            expanded = [float(it.get("expanded_nodes", 0) or 0) for it in items]
            cost = [float(it.get("compute_cost", 0.0) or 0.0) for it in items]
            robust = [float(it.get("robustness", 0.0) or 0.0) for it in items]
            n = len(items)

            def _mean(values: list) -> float:
                return round(sum(values) / n, 4) if values else 0.0

            records.append(
                {
                    "algorithm": algo,
                    "scene_level": scene_level,
                    "avg_time": round(sum(runtimes) / n, 4),
                    "avg_path_length": round(sum(lengths) / n, 2),
                    "success_rate": round(sum(successes) / n, 4),
                    "stability_score": round(sum(stab) / n, 4),
                    "smoothness": _mean(smooth),
                    "safety_score": _mean(safety),
                    "expanded_nodes": round(sum(expanded) / n),
                    "compute_cost": _mean(cost),
                    "robustness": _mean(robust),
                }
            )
        return records

    def _records_from_json(self, scene_level: str) -> List[dict]:
        return [
            dict(record)
            for record in (self.performance_db or [])
            if record.get("scene_level") == scene_level
            and record.get("algorithm") in ALLOWED_ALGORITHMS
        ]

    def retrieve(self, scene_level: str,
                 include_literature: bool = False) -> list:
        """返回指定场景等级下的算法记录列表。

        ``include_literature=True`` 时，会尝试加载 ``LiteratureAgent``
        并在每条记录上附加 ``literature_facts`` 字段。
        """
        records = self._records_from_sqlite(scene_level)
        source = "sqlite"
        if not records:
            records = self._records_from_json(scene_level)
            source = "json"

        for r in records:
            r["data_source"] = source

        if include_literature and records:
            try:
                from agents.literature_agent import LiteratureAgent
                la = LiteratureAgent()
            except Exception as exc:
                logger.warning("LiteratureAgent 加载失败: %s", exc)
                la = None

            if la is not None:
                for r in records:
                    r["literature_facts"] = la.get_paper_facts(
                        r.get("algorithm", "")
                    )

        return records

    def retrieve_state(self, state) -> "ResearchState":
        """Phase 4 入口：基于 ``state.metadata["scene_level"]`` 检索，写入 ``state.algorithm_records``。"""
        from agents.research_state import ResearchState  # 避免循环导入

        if state.metadata is None:
            state.metadata = {}
        scene_level = state.metadata.get("scene_level") or "未知"
        try:
            records = self.retrieve(scene_level, include_literature=False)
        except Exception as exc:
            logger.error("KnowledgeRetrievalAgent.retrieve 失败: %s", exc, exc_info=True)
            state.metadata.setdefault("errors", []).append(
                f"KnowledgeRetrievalAgent.retrieve 失败: {exc}"
            )
            records = []
        state.algorithm_records = records
        return state
