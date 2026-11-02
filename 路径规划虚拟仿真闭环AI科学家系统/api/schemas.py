from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EnvInputRequest(BaseModel):
    obstacle_ratio: float = Field(default=0.1, ge=0.0, le=1.0, description="障碍物占比")
    map_width: int = Field(default=30, ge=10, le=1000, description="地图宽度")
    map_height: int = Field(default=30, ge=10, le=1000, description="地图高度")
    connectivity: float = Field(default=0.68, ge=0.0, le=1.0, description="连通性")
    topology_randomness: float = Field(default=0.55, ge=0.0, le=1.0, description="拓扑随机性")
    dynamic_change_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="动态变化率")
    dynamic_steps: int = Field(default=2, ge=1, le=10, description="动态地图帧数")
    compute_limit: str = Field(default="medium", description="算力限制 (low/medium/high)")
    start_point: Optional[List[int]] = Field(default=None, description="起点坐标 [x, y]")
    target_point: Optional[List[int]] = Field(default=None, description="终点坐标 [x, y]")
    random_seed: int = 42
    optimization_preference: str = "平衡模式"
    human_feedback: str = ""
    previous_cycle_id: Optional[str] = None
    grid: Optional[List[List[int]]] = None
    max_iterations: int = Field(default=1, ge=1, le=3)


class DecisionResponse(BaseModel):
    best_algorithm: str = Field(default="", description="推荐算法名称")
    best_score: float = Field(default=0.0, description="综合得分")
    ranking: Optional[List[Dict[str, Any]]] = Field(default=None, description="算法排名列表")
    scene_level: str = Field(default="未知", description="场景等级")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="置信度")


class HypothesisResponse(BaseModel):
    hypothesis_text: str = Field(default="", description="假设正文")
    experiment_plan: Optional[str] = Field(default=None, description="实验方案")
    expected_results: Optional[str] = Field(default=None, description="预期结果")
    boundary_conditions: Optional[str] = Field(default=None, description="边界条件")


class ReportResponse(BaseModel):
    title: str = Field(default="", description="报告标题")
    abstract: Optional[str] = Field(default=None, description="摘要")
    sections: Optional[Dict[str, str]] = Field(default=None, description="报告各章节")
    references: Optional[List[str]] = Field(default=None, description="参考文献列表")


class ExperimentRequest(BaseModel):
    algorithms: List[str] = Field(..., description="关注的算法列表；核心实验始终运行全部五算法")
    map_params: Dict[str, Any] = Field(default_factory=dict, description="地图参数")
    n_runs: int = Field(default=5, ge=1, le=100, description="每个算法运行次数")
    compute_limit: str = Field(default="medium", description="算力限制")
    dynamic_change_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="动态变化率")


class ExperimentResponse(BaseModel):
    run_id: str = Field(..., description="实验运行ID")
    status: str = Field(default="pending", description="状态 (pending/running/completed/failed)")
    progress: float = Field(default=0.0, ge=0.0, le=1.0, description="进度")
    results: Optional[Dict[str, Any]] = Field(default=None, description="实验结果")
    created_at: Optional[str] = Field(default=None, description="创建时间")
