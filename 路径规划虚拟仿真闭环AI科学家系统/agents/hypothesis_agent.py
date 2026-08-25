# agents/hypothesis_agent.py — 科学假设生成智能体（Phase 5 4 段结构化版）
"""
Phase 5 提示词 5-1 升级说明
---------------------------

1. 旧版契约（Phase 0/1/4）继续保留：
   - ``HypothesisAgent.__init__(self, use_qwen: bool = True)``：仅当
     ``use_qwen=True`` 时实例化 ``QwenClient``，import 失败时降级为离线。
   - ``HypothesisAgent.generate(self, env, decision, explanation) -> str``：
     旧 3 参入口，内部委托到 ``generate_state``，返回 ``str``。
   - ``HypothesisAgent.generate_state(self, state) -> ResearchState``：
     旧 ``*_state`` 入口，内部委托到新的 ``generate(state)``。
2. 新版契约（Phase 5）：
   - ``HypothesisAgent.generate(self, state: ResearchState) -> ResearchState``：
     接收 ``ResearchState``，调用 V2 提示词（``HYPOTHESIS_SYSTEM_PROMPT_V2`` /
     ``HYPOTHESIS_USER_TEMPLATE_V2``），正则 + ``json.loads`` 解析 4 段 JSON；
     解析成功则把 ``hypothesis_text`` / ``experiment_plan`` / ``expected_results`` /
     ``boundary_conditions`` 写入 ``state.hypothesis`` 并标记 ``generated_by="qwen"``；
     解析失败回退到 ``_default_hypothesis_struct(state)`` 并把异常追加到
     ``state.metadata["errors"]``。
3. ``state.hypothesis`` 形状（4 段结构化）：
   ``hypothesis_text`` / ``experiment_plan`` / ``expected_results`` /
   ``boundary_conditions`` / ``raw_text`` / ``generated_by``，
   同时**保留** Phase 4 的 3 字段 ``text`` / ``best_algorithm`` / ``scene_level``
   以保证向后兼容。
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional

from agents.research_state import ResearchState
from llm.prompt_templates import (
    HYPOTHESIS_SYSTEM_PROMPT,
    HYPOTHESIS_SYSTEM_PROMPT_V2,
    HYPOTHESIS_USER_TEMPLATE,
    HYPOTHESIS_USER_TEMPLATE_V2,
)

logger = logging.getLogger(__name__)

# 容错：QwenClient 在没有 API key / 缺少依赖时可降级为离线规则生成
try:  # pragma: no cover - 兼容旧 import 路径
    from llm.qwen_client import QwenClient
except Exception as exc:  # pragma: no cover
    logger.warning("QwenClient 导入失败: %s", exc)
    QwenClient = None  # type: ignore[assignment]


# Phase 5 默认算法清单（与 knowledge_agent / decision_agent 知识库一致）
_DEFAULT_ALGORITHMS: List[str] = [
    "A*",
    "ACO",
    "PSO",
    "SA",
    "混合优化算法",
]

# 评估指标集合（与 evaluation_agent / ExperimentAgent 一致）
_DEFAULT_METRICS: List[str] = [
    "success_rate",
    "avg_time",
    "avg_path_length",
    "stability_score",
]

# 固定中文边界条件模板
_DEFAULT_BOUNDARY_CONDITIONS: List[str] = [
    "地图尺寸 ≥ 50×50",
    "障碍物占比 < 0.7",
    "起点与终点连通",
    "算力限制 ∈ {low, medium, high}",
]


class HypothesisAgent:
    """调用 Qwen 生成可验证科学假设（Phase 5：4 段结构化输出）。"""

    def __init__(self, use_qwen: bool = True):
        self.use_qwen = use_qwen
        self.client: Optional["QwenClient"] = None
        if use_qwen and QwenClient is not None:
            try:
                self.client = QwenClient()
            except Exception as exc:
                logger.warning("HypothesisAgent QwenClient 初始化失败: %s", exc)
                self.client = None

    # ------------------------------------------------------------------ #
    # 统一入口：根据入参类型分派到旧/新 generate
    # ------------------------------------------------------------------ #
    def generate(self, *args, **kwargs):
        """统一入口：
        - 旧调用（Phase 0/1/4）：``generate(env: dict, decision: dict, explanation: str) -> str``
        - 新调用（Phase 5）：``generate(state: ResearchState) -> ResearchState``
        """
        if len(args) == 1 and not isinstance(args[0], dict):
            state_arg = args[0]
            if isinstance(state_arg, ResearchState):
                return self._generate_struct(state_arg)
            raise TypeError(
                "HypothesisAgent.generate(state) 期望 ResearchState 类型，"
                f"实际得到 {type(state_arg).__name__}"
            )
        if len(args) == 3 and isinstance(args[0], dict):
            return self._generate_legacy(args[0], args[1], args[2])
        raise TypeError(
            "HypothesisAgent.generate 签名必须是 "
            "(env: dict, decision: dict, explanation: str) 或 "
            "(state: ResearchState) 之一"
        )

    # ------------------------------------------------------------------ #
    # 新版：Phase 5 4 段结构化（V2 入口）
    # ------------------------------------------------------------------ #
    def _generate_struct(self, state: ResearchState) -> ResearchState:
        """Phase 5 核心入口：调用 V2 提示词，解析 4 段结构化 JSON。"""
        decision = state.decision or {}
        env = state.env_input or {}

        # 调用 LLM（仅在 self.client 可用时）
        parsed: Optional[Dict[str, Any]] = None
        raw_llm_text: str = ""
        if self.use_qwen and self.client is not None and decision.get("best_algorithm"):
            try:
                raw_llm_text = self._call_qwen_v2(env, decision)
                parsed = self._parse_json_segment(raw_llm_text)
            except Exception as exc:
                logger.error("HypothesisAgent LLM 解析失败: %s", exc, exc_info=True)
                if state.metadata is None:
                    state.metadata = {}
                state.metadata.setdefault("errors", []).append(
                    f"HypothesisAgent LLM 解析失败: {exc}"
                )
                parsed = None

        if parsed is not None:
            struct = self._normalize_llm_struct(parsed, state)
            struct["generated_by"] = "qwen"
            struct["raw_text"] = raw_llm_text or self._default_hypothesis_10_fields(state)
        else:
            struct = self._default_hypothesis_struct(state)

        # 4 段结构化字段写入 state.hypothesis
        state.hypothesis = {
            "hypothesis_text": struct.get("hypothesis_text", ""),
            "experiment_plan": struct.get("experiment_plan", {}),
            "expected_results": struct.get("expected_results", {}),
            "boundary_conditions": struct.get("boundary_conditions", []),
            "raw_text": struct.get("raw_text", ""),
            "generated_by": struct.get("generated_by", "rule"),
            # ---- 向后兼容：保留 Phase 4 3 字段 ----
            "text": struct.get("raw_text", ""),
            "best_algorithm": decision.get("best_algorithm", "")
            or struct.get("expected_results", {}).get("best_algorithm", ""),
            "scene_level": decision.get("scene_level", ""),
        }
        return state

    # ------------------------------------------------------------------ #
    # 旧版：Phase 0/1/4 入口（保持字符串返回）
    # ------------------------------------------------------------------ #
    def _generate_legacy(self, env: dict, decision: dict, explanation: str) -> str:
        """旧 generate(env, decision, explanation) -> str 的实现。"""
        if not self.use_qwen or self.client is None:
            return self._default_hypothesis(env or {}, decision or {})

        # 旧调用方沿用 V1 提示词，行为与 Phase 4 完全一致
        try:
            ranking_detail = "\n".join(
                f"{r['algorithm']}: 得分={r['score']:.4f}, 成功率={r['success_rate']}"
                for r in (decision or {}).get("ranking", [])[:3]
            )
            env_detail = (
                f"障碍物占比={env.get('obstacle_ratio')}, "
                f"连通性={env.get('connectivity')}, "
                f"拓扑随机性={env.get('topology_randomness')}, "
                f"算力限制={env.get('compute_limit')}"
            )
            user_prompt = HYPOTHESIS_USER_TEMPLATE.format(
                scene_level=decision.get("scene_level", ""),
                best_algorithm=decision.get("best_algorithm", ""),
                explanation=explanation or "",
                ranking_detail=ranking_detail,
                env_detail=env_detail,
            )
            return self.client.chat(HYPOTHESIS_SYSTEM_PROMPT, user_prompt)
        except Exception as exc:
            logger.error("HypothesisAgent._call_qwen_v2 调用失败: %s", exc, exc_info=True)
            return self._default_hypothesis(env or {}, decision or {})

    def generate_state(self, state: ResearchState) -> ResearchState:
        """Phase 4 入口：基于 ``state`` 生成科学假设，写入 ``state.hypothesis``。
        内部委托到新版 ``generate(state)``。
        """
        decision = state.decision or {}
        if not decision or not decision.get("best_algorithm"):
            return state
        env = state.env_input or {}
        explanation = ""
        try:
            meta = state.metadata or {}
            expl_obj = meta.get("explanation")
            if isinstance(expl_obj, dict):
                explanation = expl_obj.get("explanation_text", "") or ""
        except Exception as exc:
            logger.warning("HypothesisAgent 提取 explanation_text 失败: %s", exc)
            explanation = ""

        try:
            # 直接调用新版 generate(state)，确保 hypothesis 写入 4 段结构化字段
            return self.generate(state)
        except Exception as exc:
            logger.error("HypothesisAgent.generate_state 失败: %s", exc, exc_info=True)
            if state.metadata is None:
                state.metadata = {}
            state.metadata.setdefault("errors", []).append(
                f"HypothesisAgent.generate_state 失败: {exc}"
            )
            # 兜底：写一个 3 字段的旧版 hypothesis，不破坏下游
            state.hypothesis = {
                "best_algorithm": decision.get("best_algorithm", ""),
                "scene_level": decision.get("scene_level", ""),
                "text": self._default_hypothesis(env, decision),
            }
            return state

    # ------------------------------------------------------------------ #
    # LLM 工具：调用 + JSON 提取
    # ------------------------------------------------------------------ #
    def _call_qwen_v2(self, env: dict, decision: dict) -> str:
        """调用 V2 提示词拿到 LLM 原始输出。"""
        assert self.client is not None
        ranking_detail = "\n".join(
            f"{r['algorithm']}: 得分={r['score']:.4f}, 成功率={r['success_rate']}"
            for r in (decision or {}).get("ranking", [])[:5]
        )
        env_detail = (
            f"障碍物占比={env.get('obstacle_ratio')}, "
            f"连通性={env.get('connectivity')}, "
            f"拓扑随机性={env.get('topology_randomness')}, "
            f"算力限制={env.get('compute_limit')}, "
            f"地图尺寸={env.get('map_width', 100)}×{env.get('map_height', 100)}"
        )
        user_prompt = HYPOTHESIS_USER_TEMPLATE_V2.format(
            scene_level=decision.get("scene_level", ""),
            best_algorithm=decision.get("best_algorithm", ""),
            ranking_detail=ranking_detail or "（无排名数据）",
            env_detail=env_detail,
        )
        return self.client.chat(HYPOTHESIS_SYSTEM_PROMPT_V2, user_prompt)

    @staticmethod
    def _parse_json_segment(text: str) -> Optional[Dict[str, Any]]:
        """用正则提取 JSON 段并解析；解析失败返回 None。"""
        if not text:
            return None
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        candidate = match.group(0)
        try:
            obj = json.loads(candidate)
        except Exception as exc:
            logger.warning("HypothesisAgent._parse_json_segment JSON 解析失败: %s", exc)
            return None
        if not isinstance(obj, dict):
            return None
        return obj

    @staticmethod
    def _normalize_llm_struct(
        parsed: Dict[str, Any], state: ResearchState
    ) -> Dict[str, Any]:
        """把 LLM 返回的 dict 规整为 4 段结构化字段，缺字段用默认补齐。"""
        decision = state.decision or {}
        env = state.env_input or {}

        # 1) hypothesis_text
        hypothesis_text = str(parsed.get("hypothesis_text") or "").strip()
        if not hypothesis_text:
            hypothesis_text = (
                "在"
                f"{decision.get('scene_level', '当前')}"
                "条件下，"
                f"{decision.get('best_algorithm', '推荐算法')}"
                "相比次优算法在成功率与耗时上有显著优势"
            )

        # 2) experiment_plan
        ep_raw = parsed.get("experiment_plan") or {}
        if not isinstance(ep_raw, dict):
            ep_raw = {}
        maps_raw = ep_raw.get("maps") or {}
        if not isinstance(maps_raw, dict):
            maps_raw = {}
        experiment_plan: Dict[str, Any] = {
            "maps": {
                "count": int(maps_raw.get("count") or 50),
                "width": int(maps_raw.get("width") or env.get("map_width") or 100),
                "height": int(maps_raw.get("height") or env.get("map_height") or 100),
                "obstacle_ratio": float(
                    maps_raw.get("obstacle_ratio")
                    if maps_raw.get("obstacle_ratio") is not None
                    else env.get("obstacle_ratio", 0.3)
                ),
            },
            "algorithms": list(ep_raw.get("algorithms") or _DEFAULT_ALGORITHMS),
            "runs_per_algorithm": int(ep_raw.get("runs_per_algorithm") or 5),
            "metrics": list(ep_raw.get("metrics") or _DEFAULT_METRICS),
        }

        # 3) expected_results
        er_raw = parsed.get("expected_results") or {}
        if not isinstance(er_raw, dict):
            er_raw = {}
        expected_results: Dict[str, Any] = {
            "best_algorithm": str(
                er_raw.get("best_algorithm")
                or decision.get("best_algorithm", "")
            ),
            "success_rate_threshold": float(
                er_raw.get("success_rate_threshold")
                if er_raw.get("success_rate_threshold") is not None
                else 0.7
            ),
            "time_budget_seconds": float(
                er_raw.get("time_budget_seconds")
                if er_raw.get("time_budget_seconds") is not None
                else 1.0
            ),
        }

        # 4) boundary_conditions
        bc_raw = parsed.get("boundary_conditions") or []
        if isinstance(bc_raw, list) and bc_raw:
            boundary_conditions = [str(x) for x in bc_raw]
        else:
            boundary_conditions = list(_DEFAULT_BOUNDARY_CONDITIONS)

        return {
            "hypothesis_text": hypothesis_text,
            "experiment_plan": experiment_plan,
            "expected_results": expected_results,
            "boundary_conditions": boundary_conditions,
        }

    # ------------------------------------------------------------------ #
    # 离线规则生成器
    # ------------------------------------------------------------------ #
    def _default_hypothesis_struct(self, state: ResearchState) -> Dict[str, Any]:
        """4 段结构化假设的离线规则生成器。"""
        decision = state.decision or {}
        env = state.env_input or {}
        best_algorithm = decision.get("best_algorithm") or "混合优化算法"
        scene_level = decision.get("scene_level") or "中复杂度"
        # 次优算法：取 ranking 第二位；若没有则回退 A*
        ranking = decision.get("ranking") or []
        second = "A*"
        for r in ranking:
            if isinstance(r, dict) and r.get("algorithm") and r["algorithm"] != best_algorithm:
                second = r["algorithm"]
                break
        obstacle_ratio = env.get("obstacle_ratio")
        try:
            obs_str = f"{float(obstacle_ratio):.0%}" if obstacle_ratio is not None else "未知"
        except Exception as exc:
            logger.warning("HypothesisAgent._default_hypothesis_struct obstacle_ratio 格式化失败: %s", exc)
            obs_str = str(obstacle_ratio)

        hypothesis_text = (
            f"在{scene_level}、障碍物占比≈{obs_str}的随机地图条件下，"
            f"算法 {best_algorithm} 相比 {second} "
            f"在 success_rate 与 avg_time 指标上具有显著优势。"
        )

        experiment_plan: Dict[str, Any] = {
            "maps": {
                "count": 50,
                "width": int(env.get("map_width") or 100),
                "height": int(env.get("map_height") or 100),
                "obstacle_ratio": (
                    float(obstacle_ratio) if obstacle_ratio is not None else 0.3
                ),
            },
            "algorithms": list(_DEFAULT_ALGORITHMS),
            "runs_per_algorithm": 5,
            "metrics": list(_DEFAULT_METRICS),
        }

        expected_results: Dict[str, Any] = {
            "best_algorithm": best_algorithm,
            "success_rate_threshold": 0.7,
            "time_budget_seconds": 1.0,
        }

        boundary_conditions = list(_DEFAULT_BOUNDARY_CONDITIONS)

        raw_text = self._default_hypothesis_10_fields(state)

        return {
            "hypothesis_text": hypothesis_text,
            "experiment_plan": experiment_plan,
            "expected_results": expected_results,
            "boundary_conditions": boundary_conditions,
            "raw_text": raw_text,
            "generated_by": "rule",
        }

    # ------------------------------------------------------------------ #
    # 旧 _default_hypothesis(env, decision) -> str 兼容入口
    # ------------------------------------------------------------------ #
    def _default_hypothesis(self, env: dict, decision: dict) -> str:
        """10 字段模板字符串：Phase 0/1 调用方仍可通过旧签名拿到文本。"""
        state = ResearchState(env_input=env or {})
        state.decision = decision or {}
        return self._default_hypothesis_10_fields(state)

    # ------------------------------------------------------------------ #
    # 10 字段模板渲染器（核心）
    # ------------------------------------------------------------------ #
    def _default_hypothesis_10_fields(self, state: ResearchState) -> str:
        """基于 ``ResearchState`` 渲染 10 字段字符串模板。

        字段：待研究问题 / 科学假设 / 解决思路 / 必要技术手段 / 数据集 /
             论文标题 / 摘要 / 方法论 / 实验设计 / 参考论文
        """
        decision = state.decision or {}
        env = state.env_input or {}
        map_features = state.map_features or {}
        literature_facts = state.literature_facts or []
        algorithm_records = state.algorithm_records or []

        scene_level = decision.get("scene_level") or "中复杂度"
        best_algorithm = decision.get("best_algorithm") or "推荐算法"
        best_score = decision.get("best_score")
        best_score_str = (
            f"{best_score:.4f}" if isinstance(best_score, (int, float)) else "N/A"
        )

        obstacle_ratio = env.get("obstacle_ratio")
        obs_str = (
            f"{float(obstacle_ratio):.0%}"
            if isinstance(obstacle_ratio, (int, float))
            else "未知"
        )
        map_width = env.get("map_width") or 100
        map_height = env.get("map_height") or 100
        connectivity = env.get("connectivity", "N/A")
        topology_randomness = env.get("topology_randomness", "N/A")
        compute_limit = env.get("compute_limit", "N/A")

        cluster_count = map_features.get("cluster_count", "N/A")
        bottleneck_count = map_features.get("bottleneck_count", "N/A")
        entropy = map_features.get("entropy", "N/A")

        algo_names = [
            r.get("algorithm")
            for r in algorithm_records
            if isinstance(r, dict) and r.get("algorithm")
        ]
        if not algo_names:
            algo_names = list(_DEFAULT_ALGORITHMS)

        lit_lines = []
        for f in literature_facts[:5]:
            if isinstance(f, dict):
                txt = f.get("fact") or f.get("text") or str(f)
                lit_lines.append(f"- {txt}")
        if not lit_lines:
            lit_lines = [
                "- A* 在静态栅格地图上路径最优但耗时随障碍密度增加而显著上升（实验数据支撑）",
                "- 混合优化算法在大规模稀疏障碍地图上成功率与耗时均优于单一启发式算法（实验数据支撑）",
            ]

        return (
            f"**待研究问题**：在{scene_level}动态随机地图中（障碍物占比≈{obs_str}，"
            f"地图尺寸 {map_width}×{map_height}），哪种路径规划算法"
            f"在成功率、平均耗时与路径长度三个维度上综合表现最优？\n\n"
            f"**科学假设**：在当前场景等级（{scene_level}）下，"
            f"{best_algorithm}（综合得分 {best_score_str}）"
            f"在历史同类场景中综合表现最优，预期其在此类环境下"
            f"具有最优的路径规划表现。\n\n"
            f"**解决思路**：基于多智能体协同的算法选型系统给出的决策，"
            f"聚焦 {best_algorithm} 与 {algo_names[0]} 等候选算法的对比，"
            f"在 50 张 {map_width}×{map_height} 随机地图上跑 5 算法 × 5 重复，"
            f"比较成功率、平均耗时、路径长度与稳定性。\n\n"
            f"**必要技术手段**：栅格地图生成、A* / ACO / PSO / SA / 混合优化算法"
            f"等 5 类基础路径规划器、统一 BenchmarkRunner、ExperimentDB 实验数据落盘、"
            f"Qwen LLM 用于假设与反思的结构化生成。\n\n"
            f"**数据集**：合成随机栅格地图（地图尺寸 {map_width}×{map_height}，"
            f"障碍物占比≈{obs_str}，连通性={connectivity}，"
            f"拓扑随机性={topology_randomness}）；地图结构特征"
            f"（cluster_count={cluster_count}，bottleneck_count={bottleneck_count}，"
            f"entropy={entropy}）。\n\n"
            f"**论文标题**：基于多智能体协同的动态栅格地图路径规划算法自适应选型研究\n\n"
            f"**摘要**：本文针对 {scene_level} 动态栅格地图下的路径规划算法选型问题，"
            f"提出一种多智能体协同的算法自适应选型方法。系统结合地图结构特征、"
            f"算力限制与历史算法表现，由 OrchestratorAgent 调度多个智能体给出最终"
            f"推荐算法（{best_algorithm}）与综合得分（{best_score_str}），"
            f"并通过 50 张随机地图上的 5 算法 × 5 重复实验验证假设。\n\n"
            f"**方法论**：数据接收 → 地图分析 → 环境建模 → 文献检索 → 事实抽取 → "
            f"知识检索 → 规则约束 → 算法评估 → 决策 → 解释 → 假设生成（4 段结构化）→ "
            f"反思 → 参数推荐；其中假设生成、实验验证、反思构成 Phase 5 的"
            f"「假设—实验—反思」闭环。\n\n"
            f"**实验设计**：50 张 {map_width}×{map_height} 随机地图，"
            f"每张地图对 { '、'.join(algo_names[:5]) } 等算法各跑 5 次，"
            f"评估指标包括 success_rate、avg_time、avg_path_length、stability_score；"
            f"算力限制={compute_limit}。\n\n"
            f"**参考论文**：\n" + "\n".join(lit_lines)
        )


__all__ = ["HypothesisAgent"]
