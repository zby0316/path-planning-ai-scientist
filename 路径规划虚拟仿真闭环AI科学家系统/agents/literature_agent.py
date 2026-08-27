# agents/literature_agent.py — 文献检索智能体

import json
import logging
import threading
from typing import Iterable, List, Optional

import requests

from literature.models import PaperRecord
from config import LITERATURE_KB_PATH

logger = logging.getLogger(__name__)

SEMANTIC_SCHOLAR_ENDPOINT = (
    "https://api.semanticscholar.org/graph/v1/paper/search"
)
SEMANTIC_SCHOLAR_FIELDS = "title,authors,year,venue,externalIds,url,abstract"


class LiteratureAgent:
    """基于本地知识库与 Semantic Scholar 的文献检索智能体。

    - 启动时将 ``literature/literature_kb.json`` 载入内存。
    - :meth:`search_local` 支持算法名 / 关键词模糊匹配。
    - :meth:`search_semantic_scholar` 通过 Semantic Scholar 公共 API 扩展检索范围，
      网络不可用时降级为仅本地搜索并记录 warning。
    - :meth:`get_paper_facts` 汇总与指定算法相关的全部事实。
    - :meth:`add_paper` 支持向本地知识库 JSON 追加新文献。
    """

    _lock = threading.Lock()

    def __init__(self, kb_path: str = LITERATURE_KB_PATH):
        self.kb_path = kb_path
        self.papers: List[PaperRecord] = []
        self._load_kb()

    def _load_kb(self) -> None:
        try:
            with open(self.kb_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
        except FileNotFoundError:
            logger.warning("文献知识库文件未找到: %s，初始化为空", self.kb_path)
            self.papers = []
            return
        except json.JSONDecodeError as exc:
            logger.error("文献知识库 JSON 解析失败: %s", exc)
            self.papers = []
            return

        items = payload.get("papers", []) if isinstance(payload, dict) else payload
        # 复核闸门：未复核/被拒的条目不得进入检索范围
        self.papers = [
            PaperRecord.from_dict(item)
            for item in items
            if isinstance(item, dict)
            and item.get("review_status", "approved") not in ("pending", "rejected")
        ]

    def _save_kb(self) -> None:
        from pathlib import Path

        Path(self.kb_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.kb_path, "w", encoding="utf-8") as f:
            json.dump(
                {"version": "1.0", "description": "路径规划算法自适应选型系统文献知识库",
                 "papers": [p.to_dict() for p in self.papers]},
                f, ensure_ascii=False, indent=2,
            )

    @staticmethod
    def _normalize(text: str) -> str:
        return (text or "").lower()

    def _match_paper(self, paper: PaperRecord, keywords: Iterable[str]) -> bool:
        keywords = [self._normalize(k) for k in keywords if k]
        if not keywords:
            return True

        haystack_parts: List[str] = [
            self._normalize(paper.title),
            self._normalize(paper.venue),
            self._normalize(paper.doi or ""),
            self._normalize(" ".join(paper.algorithm_related or [])),
            self._normalize(" ".join(paper.authors or [])),
        ]
        haystack = " | ".join(haystack_parts)

        for kw in keywords:
            if kw in haystack:
                return True
            for algo in paper.algorithm_related or []:
                if self._normalize(algo) == kw:
                    return True
        return False

    def search_local(self, keywords: Optional[List[str]] = None) -> List[PaperRecord]:
        """在本地文献知识库中按关键词模糊匹配。"""
        keywords = keywords or []
        if not keywords:
            return list(self.papers)
        return [p for p in self.papers if self._match_paper(p, keywords)]

    def search_semantic_scholar(self, query: str, limit: int = 5,
                                 timeout: float = 8.0) -> List[dict]:
        """调用 Semantic Scholar Graph API 检索文献。

        返回原始 API 结果列表（每条为 dict）。网络异常时返回空列表
        并降级为仅本地搜索模式。
        """
        if not query:
            return []

        params = {
            "query": query,
            "limit": max(1, min(limit, 20)),
            "fields": SEMANTIC_SCHOLAR_FIELDS,
        }
        headers = {"User-Agent": "ai-scientist-path-planning/1.0"}
        try:
            resp = requests.get(
                SEMANTIC_SCHOLAR_ENDPOINT,
                params=params,
                headers=headers,
                timeout=timeout,
            )
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.warning("Semantic Scholar API 不可用，降级为本地检索: %s", exc)
            return []

        data = resp.json() if resp.content else {}
        return data.get("data", []) or []

    def get_paper_facts(self, algorithm: str) -> List[str]:
        """汇总与指定算法相关的全部 key_facts，去重后返回。"""
        algo_norm = self._normalize(algorithm)
        facts: List[str] = []
        seen: set = set()
        for paper in self.papers:
            related = [self._normalize(a) for a in (paper.algorithm_related or [])]
            if algo_norm not in related and algo_norm not in self._normalize(paper.title):
                continue
            for fact in paper.key_facts or []:
                if fact and fact not in seen:
                    seen.add(fact)
                    facts.append(fact)
        return facts

    def add_paper(self, paper: PaperRecord) -> None:
        """将新文献追加到本地知识库（线程安全）。"""
        with self._lock:
            for existing in self.papers:
                if existing.paper_id == paper.paper_id:
                    logger.info("paper_id=%s 已存在，跳过追加", paper.paper_id)
                    return
            self.papers.append(paper)
            self._save_kb()

    def enrich_state(self, state) -> "ResearchState":
        """Phase 4 入口：基于当前推荐算法（若有）从本地文献库抽取相关事实。

        结果写入 ``state.literature_facts``（每项为 ``{"fact", "algorithm", "verified"}`` dict）。
        """
        from agents.research_state import ResearchState  # 避免循环导入

        decision = state.decision or {}
        best_algo = decision.get("best_algorithm", "")
        try:
            facts_text: List[str] = self.get_paper_facts(best_algo) if best_algo else []
        except Exception as exc:
            logger.error("LiteratureAgent.get_paper_facts 失败: %s", exc, exc_info=True)
            if state.metadata is None:
                state.metadata = {}
            state.metadata.setdefault("errors", []).append(
                f"LiteratureAgent.get_paper_facts 失败: {exc}"
            )
            facts_text = []

        facts: List[dict] = []
        for fact in facts_text:
            facts.append(
                {
                    "algorithm": best_algo,
                    "fact": fact,
                    "verified": True,
                }
            )
        # 合并既有 facts（不覆盖）
        existing = list(state.literature_facts or [])
        state.literature_facts = existing + facts
        return state
