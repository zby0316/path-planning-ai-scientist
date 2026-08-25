"""文献数据模型定义。

提供 PaperRecord 数据类，用于描述文献知识库中单条文献的元数据
及与之关联的算法事实、证据等级和 BibTeX 引用字符串。
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any


@dataclass
class PaperRecord:
    """文献知识库中的单条文献记录。

    Attributes:
        paper_id: 文献内部唯一标识。
        title: 文献标题。
        authors: 作者列表。
        year: 发表年份。
        venue: 会议/期刊名称。
        doi: 数字对象标识符。
        url: 文献访问链接（兜底使用）。
        algorithm_related: 该文献涉及的算法名称列表，例如 ["A*", "ACO"]。
        key_facts: 与算法相关的可引用事实陈述。
        evidence_level: 证据等级，限定为 "review" / "paper" / "benchmark"。
        citation_bibtex: 自动生成或手工填写的 BibTeX 字符串。
    """

    paper_id: str
    title: str
    authors: List[str]
    year: int
    venue: str
    doi: str
    url: str
    algorithm_related: List[str] = field(default_factory=list)
    key_facts: List[str] = field(default_factory=list)
    evidence_level: str = "paper"
    citation_bibtex: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为可序列化的字典。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PaperRecord":
        """从字典构造 PaperRecord，忽略未知字段。"""
        valid_keys = {f for f in cls.__dataclass_fields__.keys()}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)
