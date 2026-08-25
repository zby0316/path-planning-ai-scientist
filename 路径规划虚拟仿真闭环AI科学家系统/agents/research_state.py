# agents/research_state.py — 全局研究状态对象
"""贯穿所有智能体的统一数据模型（Phase 4）。

`ResearchState` 是一份贯穿 ``DataReceiverAgent`` → ``MapAnalysisAgent`` →
``EnvironmentAgent`` → ``LiteratureAgent`` → ``FactExtractionAgent`` →
``KnowledgeRetrievalAgent`` → ``RuleConstraintAgent`` →
``AlgorithmEvaluationAgent`` → ``DecisionAgent`` → ``HumanLoopAgent`` →
``ExplanationAgent`` → ``HypothesisAgent`` → ``ReflectionAgent`` → ``ParameterAgent``
完整流水线的"快照"。

为避免破坏 Phase 0 / Phase 1 既有契约，本对象
**独立于** ``env`` / ``decision`` / ``explanation`` 字典流；各智能体的旧接口
（接收 ``dict``、返回 ``dict``）保持不变，新接口均以 ``*_state(state)`` 命名。
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _now_iso() -> str:
    """返回 UTC ISO-8601 时间字符串（秒级精度，带 ``Z`` 后缀）。"""
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )


@dataclass
class ResearchState:
    """统一研究状态对象（Phase 4 多智能体协同基座）。

    字段说明
    --------
    env_input : dict
        原始环境输入（来自 ``DataReceiverAgent.validate`` 之前的输入）。
    map_features : dict, optional
        地图结构特征（``MapAnalysisAgent`` 输出），至少包含
        ``cluster_count`` / ``bottleneck_count`` / ``entropy`` /
        ``distance_to_target``。
    literature_facts : list, optional
        与当前场景/算法相关的文献事实列表。
    algorithm_records : list, optional
        从知识库 / SQLite 检索出的算法候选记录。
    scored_algorithms : list, optional
        经评分 + 惩罚后的算法排序结果。
    decision : dict, optional
        最终决策结果（``DecisionAgent`` 输出），含
        ``best_algorithm`` / ``best_score`` / ``ranking`` / ``scene_level`` 等。
    recommended_params : dict, optional
        ``ParameterAgent`` 推荐的运行参数。
    hypothesis : dict, optional
        ``HypothesisAgent`` 生成的可验证科学假设与研究计划。
    experiment_results : list, optional
        后续实验运行的结果列表（Phase 5 完善）。
    reflection : dict, optional
        ``ReflectionAgent`` 输出的反思结果（同时存于 ``metadata["reflection"]``）。
    report : str, optional
        最终研究报告（Phase 5 / Phase 6 完善）。
    metadata : dict, optional
        杂项元数据：创建时间、pipeline 版本、错误列表、人工校验原因等。
    """

    env_input: Dict[str, Any] = field(default_factory=dict)
    map_features: Optional[Dict[str, Any]] = None
    literature_facts: Optional[List[Any]] = None
    algorithm_records: Optional[List[Dict[str, Any]]] = None
    scored_algorithms: Optional[List[Dict[str, Any]]] = None
    decision: Optional[Dict[str, Any]] = None
    recommended_params: Optional[Dict[str, Any]] = None
    hypothesis: Optional[Dict[str, Any]] = None
    experiment_results: Optional[List[Any]] = None
    reflection: Optional[Dict[str, Any]] = None
    report: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {
                "created_at": _now_iso(),
                "pipeline_version": "phase-4",
            }
        else:
            self.metadata.setdefault("created_at", _now_iso())
            self.metadata.setdefault("pipeline_version", "phase-4")
        self.metadata.setdefault("errors", [])
        self.metadata.setdefault("human_check_reasons", [])

    # ------------------------------------------------------------------ #
    # 序列化
    # ------------------------------------------------------------------ #
    def to_dict(self) -> Dict[str, Any]:
        """将状态对象序列化为纯 ``dict``（不含 dataclass 类型信息）。"""
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "ResearchState":
        """从 ``to_dict`` 的输出恢复 ``ResearchState`` 实例。"""
        if not isinstance(d, dict):
            raise TypeError(f"from_dict 期望 dict，实际得到 {type(d).__name__}")
        return ResearchState(
            env_input=d.get("env_input") or {},
            map_features=d.get("map_features"),
            literature_facts=d.get("literature_facts"),
            algorithm_records=d.get("algorithm_records"),
            scored_algorithms=d.get("scored_algorithms"),
            decision=d.get("decision"),
            recommended_params=d.get("recommended_params"),
            hypothesis=d.get("hypothesis"),
            experiment_results=d.get("experiment_results"),
            reflection=d.get("reflection"),
            report=d.get("report"),
            metadata=d.get("metadata"),
        )

    # ------------------------------------------------------------------ #
    # 摘要
    # ------------------------------------------------------------------ #
    def summary(self) -> str:
        """返回关键字段的摘要字符串，便于日志/CLI 输出。"""
        decision = self.decision or {}
        metadata = self.metadata or {}
        map_features = self.map_features or {}

        scene_level = (
            decision.get("scene_level")
            or metadata.get("scene_level")
            or "N/A"
        )
        best_algorithm = decision.get("best_algorithm", "N/A")
        best_score = decision.get("best_score", "N/A")
        need_human_check = decision.get("need_human_check", False)

        cluster_count = map_features.get("cluster_count", "N/A")
        bottleneck_count = map_features.get("bottleneck_count", "N/A")
        entropy = map_features.get("entropy", "N/A")
        distance_to_target = map_features.get("distance_to_target", "N/A")

        errors = metadata.get("errors") or []
        human_check_reasons = metadata.get("human_check_reasons") or []

        lines = [
            "=== ResearchState Summary ===",
            f"scene_level           : {scene_level}",
            f"best_algorithm        : {best_algorithm}",
            f"best_score            : {best_score}",
            f"need_human_check      : {need_human_check}",
            f"map_features.cluster_count      : {cluster_count}",
            f"map_features.bottleneck_count   : {bottleneck_count}",
            f"map_features.entropy            : {entropy}",
            f"map_features.distance_to_target : {distance_to_target}",
            f"errors_count          : {len(errors)}",
            f"human_check_reasons_count: {len(human_check_reasons)}",
        ]
        if human_check_reasons:
            lines.append("human_check_reasons:")
            for reason in human_check_reasons:
                lines.append(f"  - {reason}")
        if errors:
            lines.append("errors:")
            for err in errors:
                lines.append(f"  - {err}")
        return "\n".join(lines)


__all__ = ["ResearchState"]
