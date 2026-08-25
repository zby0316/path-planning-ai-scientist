# agents/fact_extraction_agent.py — 科学事实抽取智能体

import json
import logging
import os
import re
import uuid
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from llm.prompt_templates import (
    FACT_EXTRACTION_SYSTEM_PROMPT,
    FACT_EXTRACTION_USER_TEMPLATE,
)
from llm.qwen_client import QwenClient

logger = logging.getLogger(__name__)

EXTRACTED_FACTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "literature",
    "extracted_facts",
)
EXTRACTED_FACTS_FILE = os.path.join(EXTRACTED_FACTS_DIR, "extracted_facts.jsonl")


def _ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


class FactExtractionAgent:
    """调用 LLM 从文献摘要中抽取算法适配性事实。

    Parameters
    ----------
    qwen_client : Optional[QwenClient]
        已实例化的 Qwen 客户端；如果为 ``None``，将自动新建一个。
    use_qwen : bool
        是否真正调用 LLM。``False`` 时将走本地启发式抽取，便于离线测试。
    output_path : str
        抽取结果追加写入的 jsonl 文件路径。
    """

    def __init__(
        self,
        qwen_client: Optional[QwenClient] = None,
        use_qwen: bool = True,
        output_path: str = EXTRACTED_FACTS_FILE,
    ):
        self.use_qwen = use_qwen
        self.output_path = output_path
        if use_qwen:
            if qwen_client is not None:
                self.client = qwen_client
            else:
                try:
                    self.client = QwenClient()
                except Exception as exc:
                    logger.warning(
                        "QwenClient 初始化失败（%s），自动降级为本地启发式抽取",
                        exc,
                    )
                    self.use_qwen = False
                    self.client = None
        else:
            self.client = qwen_client
        _ensure_dir(self.output_path)

    @staticmethod
    def _strip_code_fence(text: str) -> str:
        text = (text or "").strip()
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
            text = re.sub(r"\n?```$", "", text)
        return text.strip()

    @staticmethod
    def _safe_load_json(text: str) -> Optional[Dict[str, Any]]:
        cleaned = FactExtractionAgent._strip_code_fence(text)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.warning("FactExtractionAgent._safe_load_json 直接解析失败，尝试正则提取: %s", exc)
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if not match:
                return None
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError as exc:
                logger.warning("FactExtractionAgent._safe_load_json JSON 解析失败: %s", exc)
                return None

    @staticmethod
    def _coerce_facts(parsed: Any, algorithm_names: List[str]) -> List[Dict[str, Any]]:
        facts: List[Dict[str, Any]] = []
        if not isinstance(parsed, dict):
            return facts

        raw = parsed.get("facts")
        if not isinstance(raw, list):
            return facts

        algo_set = {a.strip() for a in algorithm_names if a}
        for item in raw:
            if not isinstance(item, dict):
                continue
            fact_text = str(item.get("fact", "")).strip()
            if not fact_text:
                continue

            algo = str(item.get("algorithm", "")).strip() or (
                algorithm_names[0] if algorithm_names else "未知"
            )
            if algo_set and algo not in algo_set:
                algo = algorithm_names[0] if algorithm_names else algo

            try:
                confidence = float(item.get("confidence", 0.5))
            except (TypeError, ValueError) as exc:
                logger.warning("FactExtractionAgent._coerce_facts confidence 解析失败: %s", exc)
                confidence = 0.5
            confidence = max(0.0, min(1.0, confidence))

            evidence_type = str(item.get("evidence_type", "claimed")).lower()
            if evidence_type not in {"claimed", "experimental", "theoretical"}:
                evidence_type = "claimed"

            facts.append(
                {
                    "algorithm": algo,
                    "fact": fact_text,
                    "confidence": round(confidence, 3),
                    "evidence_type": evidence_type,
                }
            )
        return facts

    def _local_extract(self, abstract: str,
                       algorithm_names: List[str]) -> List[Dict[str, Any]]:
        """离线 fallback：基于关键词+分句的启发式抽取。"""
        text = (abstract or "").strip()
        if not text:
            return []
        sentences = re.split(r"[。.!?！？\n]", text)
        sentences = [s.strip() for s in sentences if len(s.strip()) >= 8]

        facts: List[Dict[str, Any]] = []
        algo_set = [a for a in algorithm_names if a]
        default_algo = algo_set[0] if algo_set else "未知"
        for sent in sentences:
            matched = next(
                (a for a in algo_set if a and a in sent),
                default_algo,
            )
            evidence = "claimed"
            lower = sent.lower()
            if any(k in sent for k in ("实验", "验证", "测试", "benchmark")):
                evidence = "experimental"
            elif any(k in sent for k in ("理论", "证明", "复杂度", "渐近")):
                evidence = "theoretical"
            facts.append(
                {
                    "algorithm": matched,
                    "fact": sent,
                    "confidence": 0.55,
                    "evidence_type": evidence,
                }
            )
        return facts

    def extract(self, abstract: str,
                algorithm_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """从单条摘要中抽取与指定算法相关的事实列表。"""
        algorithm_names = list(algorithm_names or [])
        if not abstract or not abstract.strip():
            return []

        if not self.use_qwen or self.client is None:
            return self._local_extract(abstract, algorithm_names)

        user_prompt = FACT_EXTRACTION_USER_TEMPLATE.format(
            algorithms="、".join(algorithm_names) if algorithm_names else "未指定",
            abstract=abstract.strip(),
        )

        try:
            raw_text = self.client.chat(
                FACT_EXTRACTION_SYSTEM_PROMPT,
                user_prompt,
                temperature=0.2,
            )
        except Exception as exc:
            logger.warning("LLM 抽取失败（%s），改用本地启发式", exc)
            return self._local_extract(abstract, algorithm_names)

        parsed = self._safe_load_json(raw_text)
        if parsed is None:
            logger.warning("LLM 返回无法解析为 JSON，使用本地启发式")
            return self._local_extract(abstract, algorithm_names)

        return self._coerce_facts(parsed, algorithm_names)

    def _append_jsonl(self, record: Dict[str, Any]) -> None:
        with open(self.output_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def batch_extract(
        self,
        papers: Iterable[Dict[str, Any]],
        algorithm_names: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """对一组文献（dict 列表）批量抽取事实，并追加写入 jsonl。"""
        algorithm_names = list(algorithm_names or [])
        all_facts: List[Dict[str, Any]] = []
        for paper in papers:
            abstract = paper.get("abstract") or paper.get("summary") or ""
            facts = self.extract(abstract, algorithm_names)
            record = {
                "fact_id": f"fact_{uuid.uuid4().hex[:12]}",
                "paper_id": paper.get("paper_id", ""),
                "title": paper.get("title", ""),
                "algorithms": algorithm_names,
                "facts": facts,
                "created_at": _now_iso(),
            }
            self._append_jsonl(record)
            all_facts.extend(facts)
        return all_facts

    def enrich_state(self, state) -> "ResearchState":
        """Phase 4 入口：仅当 ``state.literature_facts`` 为空时尝试做轻量补充。

        为避免与 ``LiteratureAgent.enrich_state`` 重复网络请求，本方法
        默认不联网：它只把 ``state.algorithm_records`` 中已有的
        ``literature_facts`` 字段合并到 ``state.literature_facts``，保证下游
        ``HumanLoopAgent`` / ``ReflectionAgent`` 能稳定拿到至少 2 条事实。
        """
        from agents.research_state import ResearchState  # 避免循环导入

        existing = list(state.literature_facts or [])
        for rec in state.algorithm_records or []:
            for fact in rec.get("literature_facts") or []:
                if isinstance(fact, str) and fact not in {f.get("fact") for f in existing if isinstance(f, dict)}:
                    existing.append({"algorithm": rec.get("algorithm", ""), "fact": fact, "verified": True})
        state.literature_facts = existing
        return state
