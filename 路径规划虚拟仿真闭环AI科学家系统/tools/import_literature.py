"""受控导入 2D 栅格路径规划 Markdown 文献。

默认只输出候选清单；只有显式传入 ``--write`` 才会更新
``literature/literature_kb.json``。导入记录一律标记为待人工复核，避免 OCR
封面文本或“规划路径”等同词异义材料直接污染正式 RAG 知识库。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any


PROJECT_DIR = Path(__file__).resolve().parents[1]
WORKSPACE_DIR = PROJECT_DIR.parent
ASSETS_DIR = Path(os.getenv("ASSETS_DIR", WORKSPACE_DIR / "assets")).resolve()
DEFAULT_SOURCE_DIR = ASSETS_DIR / "literature" / "sources"
DEFAULT_KB_PATH = PROJECT_DIR / "literature" / "literature_kb.json"

PATH_PLANNING_TERMS = ("路径规划", "自主导航", "避障", "path planning")
GRID_RELEVANCE_TERMS = (
    "栅格", "地图", "移动机器人", "无人车", "智能车辆", "动态环境",
    "未知环境", "A*", "A_算法", "蚁群", "粒子群", "模拟退火",
)
OUT_OF_SCOPE_TERMS = (
    "社会工作", "行政管理", "农村路网", "智库", "软件体系结构",
    "散装食用油", "协同配送", "机械臂", "三维路径", "月表",
)
ALGORITHM_PATTERNS = {
    "A*": ("A*", "A star", "A-star", "A_算法", "A＊"),
    "ACO": ("蚁群", "ant colony", "ACO"),
    "PSO": ("粒子群", "particle swarm", "PSO"),
    "SA": ("模拟退火", "simulated annealing"),
    "混合优化算法": ("混合算法", "融合算法", "hybrid algorithm"),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _is_candidate(path: Path, content: str) -> bool:
    sample = f"{path.stem}\n{content[:5000]}".lower()
    if any(term.lower() in sample for term in OUT_OF_SCOPE_TERMS):
        return False
    has_path_topic = any(term.lower() in sample for term in PATH_PLANNING_TERMS)
    has_grid_signal = any(term.lower() in sample for term in GRID_RELEVANCE_TERMS)
    return has_path_topic and has_grid_signal


def _detect_algorithms(content: str) -> list[str]:
    lowered = content.lower()
    return [
        name
        for name, patterns in ALGORITHM_PATTERNS.items()
        if any(pattern.lower() in lowered for pattern in patterns)
    ]


def _extract_year(content: str) -> int | None:
    years = re.findall(r"(?:19|20)\d{2}", content[:6000])
    for value in years:
        year = int(value)
        if 1990 <= year <= 2030:
            return year
    return None


def _extract_doi(content: str) -> str:
    match = re.search(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", content, re.I)
    return match.group(0).rstrip(".,;，。；") if match else ""


def _extract_abstract(content: str) -> str:
    match = re.search(
        r"摘\s*要\s*[:：]?\s*(.+?)(?:\n\s*(?:关键词|关\s*键\s*词|Abstract))",
        content,
        re.S,
    )
    return re.sub(r"\s+", " ", match.group(1)).strip() if match else ""


def _record_from_file(path: Path, source_dir: Path) -> dict[str, Any]:
    content = _read_markdown(path)
    stem_parts = path.stem.split("_")
    title = stem_parts[0].strip()
    authors = [stem_parts[-1].strip()] if len(stem_parts) > 1 else []
    digest = _sha256(path)
    abstract = _extract_abstract(content)
    return {
        "paper_id": f"local_{digest[:16]}",
        "title": title,
        "authors": authors,
        "year": _extract_year(content),
        "venue": "",
        "doi": _extract_doi(content),
        "url": "",
        "algorithm_related": _detect_algorithms(f"{title}\n{abstract}\n{content[:5000]}"),
        "key_facts": [],
        "evidence_level": "unverified_local_source",
        "citation_bibtex": "",
        "abstract": abstract,
        "source_path": str(path.relative_to(source_dir.parent)),
        "source_sha256": digest,
        "review_status": "pending",
        "in_scope": "2d_grid_path_planning_candidate",
    }


def collect_candidates(source_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    seen_hashes: set[str] = set()
    for path in sorted(source_dir.glob("*.md")):
        digest = _sha256(path)
        if digest in seen_hashes:
            continue
        content = _read_markdown(path)
        if not _is_candidate(path, content):
            continue
        records.append(_record_from_file(path, source_dir))
        seen_hashes.add(digest)
    return records


def load_kb(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "version": "1.0",
            "description": "2D 栅格路径规划文献知识库",
            "papers": [],
        }
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--kb-path", type=Path, default=DEFAULT_KB_PATH)
    parser.add_argument(
        "--write",
        action="store_true",
        help="将候选记录写入知识库；省略时仅预览。",
    )
    args = parser.parse_args()

    source_dir = args.source_dir.resolve()
    kb_path = args.kb_path.resolve()
    if not source_dir.is_dir():
        raise SystemExit(f"文献目录不存在：{source_dir}")

    candidates = collect_candidates(source_dir)
    kb = load_kb(kb_path)
    existing_hashes = {
        paper.get("source_sha256")
        for paper in kb.get("papers", [])
        if paper.get("source_sha256")
    }
    new_records = [
        record for record in candidates if record["source_sha256"] not in existing_hashes
    ]

    print(f"2D 栅格候选：{len(candidates)} 篇；尚未导入：{len(new_records)} 篇")
    for record in new_records:
        algorithms = ", ".join(record["algorithm_related"]) or "待识别"
        print(f"- {record['title']} [{algorithms}] ({record['source_path']})")

    if not args.write:
        print("预览完成；未写入任何文件。人工确认后可添加 --write。")
        return 0

    kb.setdefault("papers", []).extend(new_records)
    kb_path.parent.mkdir(parents=True, exist_ok=True)
    kb_path.write_text(
        json.dumps(kb, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"已写入 {len(new_records)} 篇待复核记录：{kb_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
