# agents/citation_agent.py — 引用核验智能体

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

import requests

logger = logging.getLogger(__name__)

DOI_HEAD_TIMEOUT = 6.0
DOI_PATTERN = re.compile(r"^10\.\d{4,9}/[^\s]+$", re.IGNORECASE)


def _normalize_doi(doi: Optional[str]) -> str:
    if not doi:
        return ""
    doi = doi.strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:", "DOI:"):
        if doi.lower().startswith(prefix.lower()):
            doi = doi[len(prefix):]
    return doi.strip()


class CitationAgent:
    """负责核验文献引用真实性的智能体。

    核验规则：
    1. 缺少 ``title`` 或 ``authors`` → 标记为 invalid。
    2. 同时缺少 ``doi`` 和 ``url`` → 标记为 suspicious。
    3. 主动调用 ``https://doi.org/`` 解析 DOI；解析失败 → invalid。
    4. 全部通过 → valid。
    """

    def __init__(self, http_timeout: float = DOI_HEAD_TIMEOUT,
                 check_doi_online: bool = True):
        self.http_timeout = http_timeout
        self.check_doi_online = check_doi_online
        try:
            self._doi_session = requests.Session()
            self._doi_session.headers.update(
                {"User-Agent": "ai-scientist-citation-checker/1.0"}
            )
        except Exception as exc:
            logger.warning("CitationAgent DOI Session 初始化失败: %s", exc)
            self._doi_session = None

    def verify(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """核验单条引用，返回 ``{"status": "valid"/"suspicious"/"invalid", ...}``。"""
        result: Dict[str, Any] = {
            "status": "valid",
            "reasons": [],
            "doi_resolved": None,
        }

        if not isinstance(paper, dict) or not paper:
            result["status"] = "invalid"
            result["reasons"].append("引用为空或非字典")
            return result

        title = paper.get("title")
        authors = paper.get("authors")
        if not title or not isinstance(title, str) or not title.strip():
            result["status"] = "invalid"
            result["reasons"].append("缺少 title 字段")
        if not authors or not isinstance(authors, (list, tuple)) or len(authors) == 0:
            result["status"] = "invalid"
            result["reasons"].append("缺少 authors 字段")

        doi = _normalize_doi(paper.get("doi"))
        url = paper.get("url")
        if not doi and not url:
            if result["status"] == "valid":
                result["status"] = "suspicious"
            result["reasons"].append("同时缺少 doi 和 url")

        if doi and self.check_doi_online:
            ok, reason = self.check_doi_exists(doi)
            result["doi_resolved"] = ok
            if not ok:
                if result["status"] == "valid":
                    result["status"] = "invalid"
                result["reasons"].append(f"DOI 解析失败: {reason}")
        elif doi:
            result["doi_resolved"] = None
        else:
            result["doi_resolved"] = None

        return result

    def validate_references(self, references: List[Dict[str, Any]]) -> Dict[str, List]:
        """批量核验引用列表，返回 ``{"valid": [...], "invalid": [...]}``。

        备注：``suspicious`` 状态的引用归入 ``invalid``，调用方可通过
        每条结果中保留的 ``reasons`` 字段进一步判断其具体原因。
        """
        valid: List[Dict[str, Any]] = []
        invalid: List[Dict[str, Any]] = []

        if not references:
            return {"valid": valid, "invalid": invalid}

        for ref in references:
            check = self.verify(ref)
            enriched = dict(ref) if isinstance(ref, dict) else {"raw": ref}
            enriched["_verification"] = check
            if check["status"] == "valid":
                valid.append(enriched)
            else:
                invalid.append(enriched)
        return {"valid": valid, "invalid": invalid}

    def check_doi_exists(self, doi: str) -> Tuple[bool, str]:
        """通过 ``https://doi.org/`` HEAD 请求验证 DOI 是否可解析。"""
        doi = _normalize_doi(doi)
        if not doi:
            return False, "DOI 为空"
        if not DOI_PATTERN.match(doi):
            return False, f"DOI 格式不合法: {doi}"

        url = f"https://doi.org/{doi}"
        sess = self._doi_session or requests
        try:
            resp = sess.head(url, allow_redirects=True, timeout=self.http_timeout)
        except requests.RequestException as exc:
            logger.warning("DOI HEAD 请求异常: %s", exc)
            try:
                resp = sess.get(url, allow_redirects=True,
                                timeout=self.http_timeout, stream=True)
            except requests.RequestException as exc2:
                logger.warning("DOI GET 请求异常: %s", exc2)
                return False, f"网络错误: {exc2}"

        if 200 <= resp.status_code < 400:
            return True, f"HTTP {resp.status_code}"
        return False, f"HTTP {resp.status_code}"

    @staticmethod
    def _author_lastname(author: str) -> str:
        author = (author or "").strip()
        if not author:
            return "anon"
        parts = re.split(r"[\s,]+", author)
        return parts[-1].lower() if parts else "anon"

    def generate_bibtex(self, paper: Dict[str, Any]) -> str:
        """根据 paper 字段自动生成 BibTeX 字符串。"""
        if not isinstance(paper, dict) or not paper:
            return ""

        title = (paper.get("title") or "").strip().rstrip(".")
        authors = paper.get("authors") or []
        if isinstance(authors, str):
            authors = [a.strip() for a in re.split(r",|;| and ", authors) if a.strip()]
        year = paper.get("year")
        venue = (paper.get("venue") or paper.get("journal") or
                 paper.get("publisher") or "").strip()
        doi = _normalize_doi(paper.get("doi"))
        url = (paper.get("url") or "").strip()

        first_author = authors[0] if authors else "anon"
        lastname = re.sub(r"[^a-zA-Z]", "", self._author_lastname(first_author)) or "anon"
        first_word = (title.split(" ")[0] if title else "ref").lower()
        first_word = re.sub(r"[^a-zA-Z]", "", first_word) or "ref"
        year_str = str(year) if year else "n.d."
        key = f"{lastname}{year_str}{first_word}"

        author_field = " and ".join(str(a) for a in authors) if authors else "anon"

        bib_lines = [f"@article{{{key},"]
        bib_lines.append(f"  title={{{title}}},")
        bib_lines.append(f"  author={{{author_field}}},")
        if year:
            bib_lines.append(f"  year={{{year}}},")
        if venue:
            bib_lines.append(f"  journal={{{venue}}},")
        if doi:
            bib_lines.append(f"  doi={{{doi}}},")
        if url:
            bib_lines.append(f"  url={{{url}}},")
        bib_lines.append("}")
        return "\n".join(bib_lines)
