# reports/report_generator.py — 标准化 10 字段研究报告生成器（Phase 5）
"""严格按 10 字段模板渲染 Markdown 报告，落盘到 reports/generated_reports/。"""
from __future__ import annotations
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from agents.citation_agent import CitationAgent
from agents.research_state import ResearchState
from config import REPORTS_DIR

__all__ = ["ReportGenerator"]

_SECTION_TITLES = [
    ("1", "待研究问题 Problem Statement"),
    ("2", "解决思路 Rationale"),
    ("3", "必要技术手段 Technical Details"),
    ("4", "数据集 Datasets"),
    ("5", "论文标题 Paper Title"),
    ("6", "摘要 Paper Abstract"),
    ("7", "方法论 Methods"),
    ("8", "实验设计 Experiments"),
    ("9", "实验结果 Results"),
    ("10", "参考论文 References"),
]


def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


class ReportGenerator:
    """10 字段 Markdown 报告生成器（Phase 5）。"""

    def __init__(self, state: ResearchState) -> None:
        self.state = state

    def generate(self) -> str:
        """渲染 10 字段 Markdown 报告。"""
        state = self.state
        hypothesis = state.hypothesis or {}
        decision = state.decision or {}
        env = state.env_input or {}
        map_features = state.map_features or {}
        experiment_results = state.experiment_results or []
        literature_facts = state.literature_facts or []
        metadata = state.metadata or {}

        # 字段 1：待研究问题
        f1 = (
            hypothesis.get("hypothesis_text")
            or hypothesis.get("text")
            or "N/A"
        )
        # 字段 2：解决思路（来自 raw_text 中"解决思路"那一段；或 hypothesis_text 后半段）
        f2 = self._extract_section(hypothesis.get("raw_text", ""), "解决思路") or f1
        # 字段 3：必要技术手段
        f3 = self._extract_section(hypothesis.get("raw_text", ""), "必要技术手段") or "A* / ACO / PSO / SA / 混合优化算法"
        # 字段 4：数据集
        f4 = self._format_datasets(env, map_features)
        # 字段 5：论文标题
        f5 = self._extract_section(hypothesis.get("raw_text", ""), "论文标题") or (
            f"基于{decision.get('scene_level', '动态')}地图的"
            f"{decision.get('best_algorithm', '路径规划')}算法选型研究"
        )
        # 字段 6：摘要
        f6 = self._extract_section(hypothesis.get("raw_text", ""), "摘要") or f1
        # 字段 7：方法论
        f7 = self._extract_section(hypothesis.get("raw_text", ""), "方法论") or self._format_methods(decision, env)
        # 字段 8：实验设计
        f8 = self._format_experiment_design(hypothesis)
        # 字段 9：实验结果
        f9 = self._format_experiment_results(experiment_results, metadata)
        # 字段 10：参考论文
        f10, verification_pending = self._format_references(literature_facts)

        lines: List[str] = ["# 科学假设与研究计划", ""]
        for idx, (num, title) in enumerate(_SECTION_TITLES, start=1):
            content = [f1, f2, f3, f4, f5, f6, f7, f8, f9, f10][idx - 1]
            lines.append(f"## {num}. {title}")
            lines.append("")
            lines.append(str(content) if content else "N/A")
            lines.append("")
            if idx == 10 and verification_pending:
                lines.append("> verification_pending: true")
                lines.append("")

        # 末尾元信息
        lines.append("---")
        lines.append("")
        lines.append(f"**生成时间**：{_now_iso()}")
        lines.append(f"**系统版本**：{metadata.get('pipeline_version', 'phase-5')}")
        lines.append("")
        return "\n".join(lines)

    def save_to_file(self, filepath: Optional[str] = None) -> str:
        """落盘到 reports/generated_reports/，返回绝对路径。"""
        if filepath is None or os.path.isdir(filepath or ""):
            base_dir = filepath if (filepath and os.path.isdir(filepath)) else REPORTS_DIR
            os.makedirs(base_dir, exist_ok=True)
            filename = f"report_{_now_iso().replace(':','-')}.md"
            filepath = os.path.join(base_dir, filename)
        else:
            os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.generate())
        return os.path.abspath(filepath)

    # ---------------- helpers ---------------- #
    @staticmethod
    def _extract_section(raw_text: str, section_name: str) -> str:
        """从 10 字段 raw_text 中抽取以"**section_name**："开头的段落。"""
        if not raw_text:
            return ""
        marker = f"**{section_name}**"
        if marker not in raw_text:
            return ""
        start = raw_text.find(marker) + len(marker)
        rest = raw_text[start:].lstrip("：: \n")
        # 找到下一个"**字段名**"分隔
        end = len(rest)
        for sec, _ in _SECTION_TITLES:
            next_marker = f"**{sec}"
            pos = rest.find(next_marker)
            if 0 < pos < end:
                end = pos
        return rest[:end].strip()

    @staticmethod
    def _format_datasets(env: Dict[str, Any], map_features: Dict[str, Any]) -> str:
        parts = [
            f"- 障碍物占比：`{env.get('obstacle_ratio', 'N/A')}`",
            f"- 地图尺寸：`{env.get('map_width', 100)} × {env.get('map_height', 100)}`",
            f"- 通道连通性：`{env.get('connectivity', 'N/A')}`",
            f"- 拓扑随机性：`{env.get('topology_randomness', 'N/A')}`",
            f"- 动态变化率：`{env.get('dynamic_change_rate', 0.0)}`",
            f"- 算力限制：`{env.get('compute_limit', 'N/A')}`",
            "- 虚拟实验仪器：动态栅格地图序列，用于模拟救援机器人/无人机在变化环境中的重规划场景",
        ]
        if map_features:
            parts.append(
                f"- 地图结构特征：cluster_count={map_features.get('cluster_count', 'N/A')}, "
                f"bottleneck_count={map_features.get('bottleneck_count', 'N/A')}, "
                f"entropy={map_features.get('entropy', 'N/A')}, "
                f"distance_to_target={map_features.get('distance_to_target', 'N/A')}"
            )
        return "\n".join(parts)

    @staticmethod
    def _format_experiment_design(hypothesis: Dict[str, Any]) -> str:
        plan = hypothesis.get("experiment_plan") or {}
        maps = plan.get("maps", {}) or {}
        algos = plan.get("algorithms", []) or []
        runs = plan.get("runs_per_algorithm", 5)
        metrics = plan.get("metrics", []) or []
        lines = [
            f"- 地图数量：**{maps.get('count', 50)}** 张（{maps.get('width', 100)}×{maps.get('height', 100)}）",
            f"- 动态变化率：**{maps.get('dynamic_change_rate', 0.0)}**",
            f"- 动态时间片：**{maps.get('dynamic_steps', 1)}**",
            f"- 待比较算法：**{', '.join(algos) or 'A*, ACO, PSO, SA, 混合优化算法'}**",
            f"- 每算法重复：**{runs}** 次",
            f"- 评估指标：**{', '.join(metrics) or 'success_rate, avg_time, avg_path_length, stability_score'}**",
            "- 适配边界变量：障碍物占比、连通性、拓扑随机性、动态变化率与算力限制",
        ]
        boundary = hypothesis.get("boundary_conditions") or []
        if boundary:
            lines.append("- 边界条件：")
            for b in boundary:
                lines.append(f"  - {b}")
        return "\n".join(lines)

    @staticmethod
    def _format_experiment_results(experiment_results: List[Dict[str, Any]], metadata: Dict[str, Any]) -> str:
        if not experiment_results:
            return (
                "（暂无实验结果）\n\n"
                "**反馈迭代机制**：系统将在获得实验结果后，由 HypothesisAgent 生成假设，"
                "ExperimentAgent 运行五算法仿真，ReflectionAgent 根据结果调整下一轮实验计划。"
            )
        sorted_res = sorted(experiment_results, key=lambda r: r.get("success_rate", 0), reverse=True)
        has_dynamic = any("dynamic_change_rate" in r or "dynamic_failure_frames" in r for r in sorted_res)
        if has_dynamic:
            lines = [
                "| 算法 | 地图数 | 成功率 | 平均耗时 | 平均路径长度 | 稳定性 | 动态变化率 | 动态失败帧 |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        else:
            lines = ["| 算法 | 地图数 | 成功率 | 平均耗时 | 平均路径长度 | 稳定性 |", "| --- | --- | --- | --- | --- | --- |"]
        for r in sorted_res:
            avg_runtime = r.get("avg_runtime", r.get("avg_time", 0))
            base = (
                f"| {r.get('algorithm', '?')} | {r.get('n_maps', 'N/A')} | "
                f"{r.get('success_rate', 0):.2f} | {avg_runtime:.4f}s | "
                f"{r.get('avg_path_length', 0):.2f} | {r.get('stability_score', 0):.4f} |"
            )
            if has_dynamic:
                base = (
                    base[:-1]
                    + f" {r.get('dynamic_change_rate', 0.0)} | "
                    + f"{r.get('dynamic_failure_frames', 0)} |"
                )
            lines.append(base)
        supported = metadata.get("hypothesis_supported")
        if supported is not None:
            verdict = "假设得到支持" if supported else "假设未得到支持"
            lines.append("")
            lines.append(f"**验证结论**：{verdict}")
            if "hypothesis_support_score" in metadata:
                lines.append(f"**支持度评分**：{metadata['hypothesis_support_score']:.3f}")
        iterations = metadata.get("iterations") or []
        lines.append("")
        lines.append(
            "**反馈迭代说明**：以上结果用于判断推荐算法的适配边界，"
            "当置信度不足或假设未被支持时，系统会把反思建议写入下一轮实验计划。"
        )
        if iterations:
            lines.append("")
            lines.append("**迭代记录**：")
            for item in iterations:
                lines.append(
                    f"- 第 {item.get('iteration', '?')} 轮："
                    f"confidence={item.get('confidence_score', 'N/A')}，"
                    f"supported={item.get('hypothesis_supported', 'N/A')}"
                )
        return "\n".join(lines)

    @staticmethod
    def _format_methods(decision: Dict[str, Any], env: Dict[str, Any]) -> str:
        return (
            "以动态栅格地图作为虚拟仿真实验仪器，围绕障碍物占比、连通性、"
            "拓扑随机性、动态变化率和算力限制构造路径规划算法适配边界；"
            f"系统先由多智能体流水线给出 {decision.get('best_algorithm', '推荐算法')} "
            f"在 {decision.get('scene_level', '当前场景')} 下的候选结论，"
            "再通过 A*、ACO、PSO、SA、混合优化算法的可复现实验进行验证，"
            "最后由反思智能体根据实验反馈调整下一轮假设和仿真计划。"
        )

    @staticmethod
    def _format_references(literature_facts: List[Any]) -> tuple:
        """调 CitationAgent 过滤 valid；网络不可用时降级并标注 verification_pending。"""
        if not literature_facts:
            return "（暂无参考文献）", False
        # 把 literature_facts 转成 validate_references 期望的 ref dict
        refs_for_check: List[Dict[str, Any]] = []
        for fact in literature_facts:
            if isinstance(fact, dict):
                # 如果已是引用 dict（有 title/authors/doi 字段）
                if "title" in fact or "authors" in fact or "doi" in fact:
                    refs_for_check.append(fact)
                # 否则把它包装成简易 ref
                else:
                    refs_for_check.append({
                        "title": str(fact.get("fact") or fact.get("title") or ""),
                        "authors": fact.get("authors", []),
                        "doi": fact.get("doi"),
                        "url": fact.get("url"),
                        "year": fact.get("year"),
                        "venue": fact.get("venue") or fact.get("journal"),
                    })
            else:
                refs_for_check.append({"title": str(fact)})
        try:
            # check_doi_online=False 避免外网请求
            agent = CitationAgent(check_doi_online=False)
            result = agent.validate_references(refs_for_check)
            valid = result.get("valid", [])
            invalid = result.get("invalid", [])
        except Exception:
            valid, invalid = refs_for_check, []
        if not valid:
            # 全部回退，并标注 verification_pending
            lines = []
            for i, ref in enumerate(refs_for_check, 1):
                title = (ref.get("title") if isinstance(ref, dict) else str(ref)) or "N/A"
                authors = ref.get("authors", []) if isinstance(ref, dict) else []
                year = ref.get("year", "n.d.") if isinstance(ref, dict) else "n.d."
                lines.append(f"{i}. {', '.join(authors) if authors else 'anon'} ({year}). *{title}*.")
            return "\n".join(lines), True
        lines = []
        for i, ref in enumerate(valid, 1):
            title = (ref.get("title") if isinstance(ref, dict) else str(ref)) or "N/A"
            authors = ref.get("authors", []) if isinstance(ref, dict) else []
            year = ref.get("year", "n.d.") if isinstance(ref, dict) else "n.d."
            doi = ref.get("doi") if isinstance(ref, dict) else None
            tail = f" DOI: {doi}" if doi else ""
            lines.append(f"{i}. {', '.join(authors) if authors else 'anon'} ({year}). *{title}*.{tail}")
        if invalid:
            lines.append("")
            lines.append(f"_（另有 {len(invalid)} 条引用因 DOI 核验未通过或字段缺失未纳入）_")
        return "\n".join(lines), False
