# tools/review_literature.py — 文献人工复核流转工具
"""对 literature/literature_pending.json 中的待复核文献执行人工复核流转。

流转规则：
- --checklist            生成 Markdown 复核清单（人工填写槽位）
- --approve <paper_id>   复核通过：从暂存区移入可信库 literature_kb.json，
                         盖 reviewed_by / reviewed_at 章，证据等级升级
- --reject <paper_id>    复核拒绝：留在暂存区并标记 rejected（附原因），
                         永不进入可信库
- --status               查看暂存区/可信库统计

只有 --approve 的记录才会进入 LiteratureAgent 的检索范围（复核闸门）。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

DEFAULT_PENDING_PATH = PROJECT_DIR / "literature" / "literature_pending.json"
DEFAULT_KB_PATH = PROJECT_DIR / "literature" / "literature_kb.json"
DEFAULT_CHECKLIST_PATH = PROJECT_DIR / "literature" / "review_checklist.md"

VALID_EVIDENCE_LEVELS = ("review", "paper", "benchmark")


def _load(path: Path) -> dict:
    if not path.exists():
        return {"version": "1.0", "papers": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _find(pending: dict, paper_id: str) -> tuple[int, dict] | None:
    for idx, paper in enumerate(pending.get("papers", [])):
        if paper.get("paper_id") == paper_id:
            return idx, paper
    return None


def cmd_status(pending: dict, kb: dict) -> int:
    papers = pending.get("papers", [])
    counts: dict[str, int] = {}
    for p in papers:
        counts[p.get("review_status", "pending")] = counts.get(p.get("review_status", "pending"), 0) + 1
    print(f"可信库（{DEFAULT_KB_PATH.name}）：{len(kb.get('papers', []))} 篇")
    print(f"暂存区（{DEFAULT_PENDING_PATH.name}）：{len(papers)} 篇 {counts or ''}")
    for p in papers:
        print(f"  [{p.get('review_status', 'pending')}] {p.get('paper_id')} — {p.get('title')}")
    return 0


def cmd_checklist(pending: dict, out_path: Path) -> int:
    todo = [p for p in pending.get("papers", []) if p.get("review_status") == "pending"]
    lines = [
        "# 文献人工复核清单",
        "",
        f"生成时间：{_now_iso()}  待复核：{len(todo)} 篇",
        "",
        "复核要点：核对标题/作者/年份/DOI 与原文一致；确认研究对象为 2D 栅格路径规划；",
        "确认算法标签正确；补录 venue / key_facts（可引用事实陈述）；判断证据等级。",
        "",
    ]
    for p in todo:
        lines += [
            f"## {p.get('title')} (`{p.get('paper_id')}`)",
            "",
            f"- 来源文件：`{p.get('source_path')}`",
            f"- 自动抽取 — 标题：{p.get('title')}",
            f"- 自动抽取 — 作者：{', '.join(p.get('authors') or []) or '（待补）'}",
            f"- 自动抽取 — 年份：{p.get('year') or '（待补）'}",
            f"- 自动抽取 — DOI：{p.get('doi') or '（待补）'}",
            f"- 自动识别 — 算法：{', '.join(p.get('algorithm_related') or []) or '（待识别）'}",
            f"- 摘要片段：{(p.get('abstract') or '（无）')[:200]}",
            "",
            "人工复核（复核者填写）：",
            "",
            "| 项目 | 结论 |",
            "|---|---|",
            "| 标题/作者/年份/DOI 正确 | ☐ 是 ☐ 否（更正：______） |",
            "| 属于 2D 栅格路径规划 | ☐ 是 ☐ 否 |",
            "| 算法标签正确 | ☐ 是 ☐ 否（更正：______） |",
            "| venue（期刊/会议） | ______ |",
            "| key_facts（可引用事实，1-3 条） | ______ |",
            "| 证据等级 | ☐ review ☐ paper ☐ benchmark |",
            "| 复核结论 | ☐ approve ☐ reject（原因：______） |",
            "",
        ]
    lines += [
        "---",
        "",
        "复核完成后执行：",
        "",
        "```powershell",
        "python tools/review_literature.py --approve <paper_id> --reviewer <姓名>",
        "python tools/review_literature.py --reject <paper_id> --reviewer <姓名> --notes <原因>",
        "```",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"复核清单已生成：{out_path}（{len(todo)} 篇待复核）")
    return 0


def cmd_approve(pending: dict, kb: dict, paper_id: str, reviewer: str,
                evidence_level: str, notes: str) -> int:
    hit = _find(pending, paper_id)
    if hit is None:
        print(f"未在暂存区找到 paper_id={paper_id}")
        return 1
    idx, paper = hit
    if paper.get("review_status") == "rejected":
        print(f"{paper_id} 已被拒绝；如需复活请先人工修改暂存区。")
        return 1

    paper["review_status"] = "approved"
    paper["reviewed_by"] = reviewer
    paper["reviewed_at"] = _now_iso()
    paper["reviewer_notes"] = notes
    paper["evidence_level"] = evidence_level

    pending["papers"].pop(idx)
    kb.setdefault("papers", []).append(paper)
    _save(DEFAULT_PENDING_PATH, pending)
    _save(DEFAULT_KB_PATH, kb)
    print(f"已复核通过并入可信库：{paper_id}（{paper['title']}）")
    print(f"复核人：{reviewer}；证据等级：{evidence_level}")
    return 0


def cmd_reject(pending: dict, paper_id: str, reviewer: str, notes: str) -> int:
    hit = _find(pending, paper_id)
    if hit is None:
        print(f"未在暂存区找到 paper_id={paper_id}")
        return 1
    _, paper = hit
    paper["review_status"] = "rejected"
    paper["reviewed_by"] = reviewer
    paper["reviewed_at"] = _now_iso()
    paper["reviewer_notes"] = notes
    _save(DEFAULT_PENDING_PATH, pending)
    print(f"已拒绝（保留在暂存区备查，不入可信库）：{paper_id}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checklist", action="store_true", help="生成 Markdown 复核清单")
    parser.add_argument("--checklist-out", type=Path, default=DEFAULT_CHECKLIST_PATH)
    parser.add_argument("--approve", metavar="PAPER_ID")
    parser.add_argument("--reject", metavar="PAPER_ID")
    parser.add_argument("--reviewer", default="", help="复核人姓名（必填于 approve/reject）")
    parser.add_argument("--notes", default="", help="复核备注/拒绝原因")
    parser.add_argument(
        "--evidence-level", default="paper", choices=VALID_EVIDENCE_LEVELS,
        help="复核通过时的证据等级（默认 paper）",
    )
    parser.add_argument("--status", action="store_true", help="查看统计")
    args = parser.parse_args()

    pending = _load(DEFAULT_PENDING_PATH)
    kb = _load(DEFAULT_KB_PATH)

    if args.status:
        return cmd_status(pending, kb)
    if args.checklist:
        return cmd_checklist(pending, args.checklist_out)
    if args.approve:
        if not args.reviewer:
            print("--approve 需要同时提供 --reviewer <姓名>（复核留痕）")
            return 1
        return cmd_approve(pending, kb, args.approve, args.reviewer,
                           args.evidence_level, args.notes)
    if args.reject:
        if not args.reviewer:
            print("--reject 需要同时提供 --reviewer <姓名>（复核留痕）")
            return 1
        return cmd_reject(pending, args.reject, args.reviewer, args.notes)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
