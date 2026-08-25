# Checklist（Phase 4 多智能体协同升级）

> 验证方法：每个条目在实现完成后由 Sub-Agent 或主流程实际执行/审阅，并通过在条目开头勾选 `[x]` 标记通过。

## ResearchState 全局状态对象（提示词 4-1）

- [x] `agents/research_state.py` 存在并实现 `ResearchState` dataclass
- [x] `ResearchState` 包含 12 个字段：`env_input` / `map_features` / `literature_facts` / `algorithm_records` / `scored_algorithms` / `decision` / `recommended_params` / `hypothesis` / `experiment_results` / `reflection` / `report` / `metadata`
- [x] 构造时 `__post_init__` 自动初始化 `metadata = {"created_at": <ISO-8601>, "pipeline_version": "phase-4"}`
- [x] `to_dict()` / `from_dict(d)` 序列化方法存在且 `to_dict() → from_dict()` 往返一致
- [x] `summary()` 方法返回非空字符串，至少包含 `scene_level` / `best_algorithm` / `best_score` / `need_human_check` / `cluster_count` / `bottleneck_count` / `entropy` / `distance_to_target` / `errors_count` / `human_check_reasons_count`
- [x] `python -c "from agents.research_state import ResearchState; rs=ResearchState(env_input={'test':True}); print(rs.summary())"` 输出非空摘要

## MapAnalysisAgent 地图结构分析（提示词 4-2）

- [x] `agents/map_analysis_agent.py` 存在并实现 `MapAnalysisAgent` 类
- [x] `MapAnalysisAgent.analyze_grid(grid)` 返回 `cluster_count` / `largest_free_ratio` / `bottleneck_count` / `entropy` 四个键
- [x] `MapAnalysisAgent.extract_features(grid, start, target)` 整合 `MapAnalyzer.analyze` 与 `analyze_grid` 的全部字段
- [x] `MapAnalysisAgent.analyze(state: ResearchState)` 接收 `ResearchState`，从 `state.map_features["grid"]` 或 `state.env_input["map_filepath"]` 取栅格，结果合并到 `state.map_features` 后返回 `state`
- [x] `map/map_analyzer.py` 的 `MapAnalyzer.analyze` **保留** 7 个既有字段（`scene_level` / `complexity_index` / `obstacle_ratio` / `start` / `target` / `free_space_ratio` / `total_cells`），**追加** 4 个新字段（`cluster_count` / `bottleneck_count` / `entropy` / `distance_to_target`）
- [x] 缺失底层依赖时（`scipy` 不可用）4 个新字段 SHALL 降级为占位值 0 / 0 / 0.0 / Manhattan 距离，不抛错
- [x] `python -c "from agents.map_analysis_agent import MapAnalysisAgent; import numpy as np; ma=MapAnalysisAgent(); f=ma.extract_features(np.zeros((20,20),dtype=np.int8),(0,0),(19,19)); print('bottleneck_count' in f)"` 输出 `True`
- [x] 构造 `ResearchState` 含 `map_features={'grid':[[0,0],[0,0]]}` 调用 `analyze` 后 `state.map_features["entropy"]` 存在

## Orchestrator 12 智能体流水线（提示词 4-3）

- [x] `agents/orchestrator_agent.py` 的 `OrchestratorAgent.__init__` 实例化全部 14 个智能体属性
- [x] `OrchestratorAgent.run(env_input) -> ResearchState` 按 spec 顺序串联 12 个步骤
- [x] 每个步骤用 `try/except` 包裹，失败时把异常追加到 `state.metadata["errors"]` 并继续执行
- [x] 现有 `DataReceiverAgent` / `EnvironmentAgent` / `KnowledgeRetrievalAgent` / `RuleConstraintAgent` / `AlgorithmEvaluationAgent` / `DecisionAgent` / `ExplanationAgent` / `HypothesisAgent` / `ParameterAgent` / `HumanLoopAgent` 既有方法签名保持不变
- [x] 上述每个智能体**追加** `*_state(state) -> ResearchState` 入口，不影响旧调用
- [x] `LiteratureAgent` / `FactExtractionAgent` 追加 `enrich_state(state)` 入口
- [x] `python -c "from agents.orchestrator_agent import OrchestratorAgent; o=OrchestratorAgent(); result=o.run({'obstacle_ratio':0.35,'map_width':100,'map_height':100,'connectivity':0.68,'topology_randomness':0.55,'compute_limit':'medium'}); print(type(result).__name__)"` 输出 `ResearchState`
- [x] `python main.py` 正常运行（`PathPlanningDecisionSystem.decide` 不被破坏，3 组场景输出排名详情）
- [x] `python -m pytest tests/ -v` 既有测试全部通过

## HumanLoopAgent 7 条件触发（提示词 4-4）

- [x] `agents/human_loop_agent.py` 保留旧接口 `check(decision: dict) -> dict`（1 条件 SCORE_GAP 行为不变）
- [x] 新增 `check_state(state: ResearchState) -> ResearchState` 接口
- [x] 7 种触发条件全部实现：①前两名得分差 < `SCORE_GAP_THRESHOLD` ②知识库中场景等级无记录 ③推荐算法与 benchmark 最优算法不一致 ④高复杂度下全部算法 `success_rate<0.5` ⑤`env_input["user_preference"]` 属于 `{"safety_first","time_first","success_first"}` ⑥`len(literature_facts)<2` ⑦存在 `verified==False` 的文献
- [x] 每条命中原因追加到 `state.metadata["human_check_reasons"]` 列表（中文描述）
- [x] `human_check_reasons` 非空时 `state.decision["need_human_check"] = True`
- [x] 构造边界输入（`algorithm_records` 空、`success_rate<0.5`、`user_preference`、`literature_facts<2`、`verified==False`）验证至少 4 种条件能命中
- [x] `python -m pytest tests/test_decision_agent.py -v` 既有测试不受影响

## ReflectionAgent 决策反思（提示词 4-5）

- [x] `agents/reflection_agent.py` 存在并实现 `ReflectionAgent` 类
- [x] `llm/prompt_templates.py` 末尾追加 `REFLECTION_SYSTEM_PROMPT` 与 `REFLECTION_USER_TEMPLATE`
- [x] `ReflectionAgent.__init__(qwen_client=None, use_qwen=True)` 仅在 `use_qwen=True` 时实例化 QwenClient
- [x] `reflect(state)` 方法实现 7 项反思检查并把结果写入 `state.metadata["reflection"]` 与 `state.reflection`
- [x] `_rule_reflect(state)` 离线回退：默认 `confidence_score=0.6` / `passed=True`；命中硬伤时 `passed=False` 且 `confidence_score<=0.4`
- [x] 输出格式符合 `{"confidence_score": float, "issues": list[str], "suggestions": list[str], "passed": bool}`
- [x] `python -c "from agents.reflection_agent import ReflectionAgent; ra=ReflectionAgent(use_qwen=False); from agents.research_state import ResearchState; rs=ResearchState(env_input={'test':True}); rs.decision={'best_algorithm':'A*','scene_level':'高复杂度','ranking':[]}; result=ra.reflect(rs); print(result.metadata.get('reflection'))"` 输出非空反思 dict
- [x] `state.algorithm_records=[]` 且 `use_qwen=False` 时 `result.metadata["reflection"]["passed"] == False` 且 `issues` 包含"知识库为空"类描述

## 模块导出（提示词 4-1 ~ 4-5）

- [x] `agents/__init__.py` 导出 `ResearchState`
- [x] `agents/__init__.py` 导出 `MapAnalysisAgent`
- [x] `agents/__init__.py` 导出 `ReflectionAgent`
- [x] `python -c "from agents import ResearchState, MapAnalysisAgent, ReflectionAgent, OrchestratorAgent, HumanLoopAgent; print('imports OK')"` 输出 `imports OK`

## 整体收口

- [x] Phase 0 / Phase 1 既有所有验证命令全部通过（`python main.py`、`python -c "import config; print('config OK')"`、`python -c "from agents.data_agent import DataReceiverAgent; ..."`）
- [x] `python -m pytest tests/ -v` 全部通过（21/21）
- [x] `agents/orchestrator_agent.py` 与 `agents/human_loop_agent.py` 旧接口（`run` 旧 dict 返回 / `check(decision)`）均保留，旧调用方不被破坏
- [x] `map/map_analyzer.py` 既有 7 字段保持不变，新字段以"追加"方式引入
- [x] 实现阶段所有 Sub-Agent 任务均按 tasks.md 执行完毕
