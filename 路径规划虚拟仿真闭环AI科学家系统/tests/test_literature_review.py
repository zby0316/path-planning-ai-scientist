# tests/test_literature_review.py — 文献复核流转回归

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import tools.review_literature as rl  # noqa: E402
from agents.literature_agent import LiteratureAgent  # noqa: E402
from literature.models import PaperRecord  # noqa: E402


@pytest.fixture()
def workspace(tmp_path, monkeypatch):
    pending = tmp_path / "literature_pending.json"
    kb = tmp_path / "literature_kb.json"
    pending.write_text(json.dumps({
        "version": "1.0",
        "papers": [
            {
                "paper_id": "local_good", "title": "好论文", "authors": ["张三"],
                "year": 2023, "venue": "", "doi": "10.1000/x", "url": "",
                "algorithm_related": ["A*"], "key_facts": [],
                "evidence_level": "unverified_local_source", "citation_bibtex": "",
                "abstract": "摘要", "source_path": "sources/好论文_张三.md",
                "source_sha256": "aaa", "review_status": "pending",
                "in_scope": "2d_grid_path_planning_candidate",
            },
            {
                "paper_id": "local_bad", "title": "离题论文", "authors": ["李四"],
                "year": 2022, "venue": "", "doi": "", "url": "",
                "algorithm_related": [], "key_facts": [],
                "evidence_level": "unverified_local_source", "citation_bibtex": "",
                "abstract": "", "source_path": "sources/离题论文_李四.md",
                "source_sha256": "bbb", "review_status": "pending",
                "in_scope": "2d_grid_path_planning_candidate",
            },
        ],
    }, ensure_ascii=False), encoding="utf-8")
    kb.write_text(json.dumps({"version": "1.0", "papers": []}, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(rl, "DEFAULT_PENDING_PATH", pending)
    monkeypatch.setattr(rl, "DEFAULT_KB_PATH", kb)
    return pending, kb


class TestReviewWorkflow:
    def test_approve_moves_to_kb_with_provenance(self, workspace):
        pending_path, kb_path = workspace
        rc = rl.cmd_approve(
            rl._load(pending_path), rl._load(kb_path),
            "local_good", reviewer="审稿人甲", evidence_level="paper", notes="已核对 DOI",
        )
        assert rc == 0
        pending = json.loads(pending_path.read_text(encoding="utf-8"))
        kb = json.loads(kb_path.read_text(encoding="utf-8"))
        assert len(pending["papers"]) == 1
        assert len(kb["papers"]) == 1
        paper = kb["papers"][0]
        assert paper["review_status"] == "approved"
        assert paper["reviewed_by"] == "审稿人甲"
        assert paper["reviewed_at"]
        assert paper["evidence_level"] == "paper"

    def test_reject_stays_out_of_kb(self, workspace):
        pending_path, kb_path = workspace
        rc = rl.cmd_reject(
            rl._load(pending_path), "local_bad",
            reviewer="审稿人甲", notes="研究对象不是栅格路径规划",
        )
        assert rc == 0
        pending = json.loads(pending_path.read_text(encoding="utf-8"))
        kb = json.loads(kb_path.read_text(encoding="utf-8"))
        assert len(kb["papers"]) == 0
        rejected = [p for p in pending["papers"] if p["paper_id"] == "local_bad"][0]
        assert rejected["review_status"] == "rejected"
        assert rejected["reviewer_notes"]

    def test_rejected_cannot_be_approved(self, workspace):
        pending_path, kb_path = workspace
        rl.cmd_reject(rl._load(pending_path), "local_bad", reviewer="甲", notes="x")
        rc = rl.cmd_approve(
            rl._load(pending_path), rl._load(kb_path),
            "local_bad", reviewer="乙", evidence_level="paper", notes="",
        )
        assert rc == 1

    def test_checklist_generated(self, workspace, tmp_path):
        pending_path, _ = workspace
        out = tmp_path / "checklist.md"
        rc = rl.cmd_checklist(rl._load(pending_path), out)
        assert rc == 0
        content = out.read_text(encoding="utf-8")
        assert "好论文" in content and "复核结论" in content

    def test_agent_gate_filters_unreviewed(self, workspace, monkeypatch):
        """复核闸门：pending/rejected 条目不得进入 LiteratureAgent 检索。"""
        _, kb_path = workspace
        # 将 pending + rejected 状态条目直接塞进 KB 文件（模拟违规写入）
        papers = [
            {"paper_id": "p1", "title": "正规", "authors": [], "year": 2020,
             "venue": "", "doi": "", "url": ""},
            {"paper_id": "p2", "title": "未复核", "authors": [], "year": 2021,
             "venue": "", "doi": "", "url": "", "review_status": "pending"},
            {"paper_id": "p3", "title": "被拒", "authors": [], "year": 2022,
             "venue": "", "doi": "", "url": "", "review_status": "rejected"},
        ]
        kb_path.write_text(json.dumps({"papers": papers}, ensure_ascii=False), encoding="utf-8")
        agent = LiteratureAgent(kb_path=str(kb_path))
        ids = {p.paper_id for p in agent.papers}
        assert ids == {"p1"}

    def test_paper_record_roundtrip_provenance(self):
        data = {
            "paper_id": "x", "title": "t", "authors": [], "year": 2020,
            "venue": "", "doi": "", "url": "", "abstract": "摘要",
            "source_path": "a.md", "source_sha256": "h",
            "review_status": "approved", "reviewed_by": "我",
        }
        rec = PaperRecord.from_dict(data)
        d = rec.to_dict()
        assert d["reviewed_by"] == "我"
        assert d["review_status"] == "approved"
        # 旧版条目（无新字段）仍可构造，默认 approved
        legacy = PaperRecord.from_dict({
            "paper_id": "y", "title": "t2", "authors": [], "year": 1990,
            "venue": "", "doi": "", "url": "",
        })
        assert legacy.review_status == "approved"
