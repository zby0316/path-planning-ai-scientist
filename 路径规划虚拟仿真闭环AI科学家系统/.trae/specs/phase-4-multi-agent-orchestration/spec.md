# Phase 4：多智能体协同升级 Spec

## Why

当前系统已具备基础的多智能体骨架（`agents/` 下含 `DataReceiverAgent` / `EnvironmentAgent` / `KnowledgeRetrievalAgent` / `RuleConstraintAgent` / `AlgorithmEvaluationAgent` / `DecisionAgent` / `ExplanationAgent` / `HumanLoopAgent` / `HypothesisAgent` 等），但 `OrchestratorAgent` 仅串联 9 个智能体、且各智能体之间以"私有 dict"为载体传递数据（`env` / `decision` / `explanation` / `hypothesis` 形态各异），缺少一个统一、显式、可序列化的全局状态对象；同时 `HumanLoopAgent` 仅判断 1 种触发条件、`EnvironmentAgent` 与地图结构分析功能耦合、整体缺少对决策结果进行反思质疑的智能体。这导致后续阶段（实验运行、报告生成、闭环修正）难以稳定地复用与回放中间状态，也无法在出现边缘情况时主动触发人工干预或自我反思。需要在本阶段引入统一的 `ResearchState` 数据模型、将地图结构分析拆为独立智能体、把 `OrchestratorAgent` 升级为 12 智能体全流水线调度器、把 `HumanLoopAgent` 触发条件扩展到 7 种、并新增 `ReflectionAgent` 对决策结果进行可信度审查。

## What Changes

- 新建 `agents/research_state.py` 中的 `ResearchState` dataclass 作为贯穿所有智能体的统一数据模型，提供 `to_dict` / `from_dict` 序列化与 `summary` 摘要方法（提示词 4-1）。
- 新建 `agents/map_analysis_agent.py` 中的 `MapAnalysisAgent`，把地图结构特征（障碍物聚类、瓶颈通道、空间分布熵、曼哈顿距离）从 `environment_agent` 中拆出，并扩展 `map/map_analyzer.py` 的 `MapAnalyzer.analyze` 以新增 `cluster_count` / `bottleneck_count` / `entropy` / `distance_to_target` 字段（提示词 4-2）。
- 重写 `agents/orchestrator_agent.py` 中的 `OrchestratorAgent`：`__init__` 实例化 12 个智能体（`DataAgent` / `MapAnalysisAgent` / `EnvironmentAgent` / `LiteratureAgent` / `FactExtractionAgent` / `KnowledgeAgent` / `RuleAgent` / `EvaluationAgent` / `ParameterAgent` / `DecisionAgent` / `HypothesisAgent` / `ReflectionAgent` 等），`run(env_input)` 返回 `ResearchState`；每个智能体的 `*` 方法接收/返回 `ResearchState`；中间步骤失败时把异常追加到 `state.metadata["errors"]` 并继续执行（提示词 4-3）。
- 重写 `agents/human_loop_agent.py`：`check(state)` 接收 `ResearchState`，按 7 种触发条件（前两名得分差、知识库缺历史数据、推荐与 benchmark 不一致、高复杂度下全部算法成功率 < 0.5、用户权重偏好、文献事实 < 2 条、引用含无法核验文献）判断 `need_human_check`，每条原因追加到 `state.metadata["human_check_reasons"]`，并将 `state.decision["need_human_check"]` 同步置为 `True`（提示词 4-4）。
- 新建 `agents/reflection_agent.py` 中的 `ReflectionAgent`：`reflect(state)` 对决策结果进行 7 项反思检查，输出 `{"confidence_score": 0~1, "issues": [...], "suggestions": [...], "passed": bool}`，并提供 `_rule_reflect(state)` 离线回退；在 `llm/prompt_templates.py` 中新增 `REFLECTION_SYSTEM_PROMPT` 与 `REFLECTION_USER_TEMPLATE`（提示词 4-5）。
- 更新 `agents/__init__.py` 导出 `ResearchState` / `MapAnalysisAgent` / `ReflectionAgent`；保留对 `OrchestratorAgent` / `HumanLoopAgent` / `ParameterAgent` / `LiteratureAgent` / `FactExtractionAgent` / `DecisionAgent` / `ExplanationAgent` 等的原有导出。
- 保留 `main.py` 的 `PathPlanningDecisionSystem.decide` 与现有 `tests/test_decision_agent.py` 行为不变（不破外既有契约），仅在 `OrchestratorAgent.run` 中通过 `ResearchState` 串联完整流水线。

## Impact

- Affected specs：
  - `phase-0-compliance-and-baseline`：受间接影响（`data_agent.validate` 行为不变）。
  - `phase-1-data-input-upgrade`：受间接影响（`DataReceiverAgent.validate` 行为不变，文件输入仍走 `MapParser`）。
- Affected code：
  - `agents/research_state.py`（新建）
  - `agents/map_analysis_agent.py`（新建）
  - `agents/reflection_agent.py`（新建）
  - `agents/orchestrator_agent.py`（重写：12 智能体流水线 + `ResearchState`）
  - `agents/human_loop_agent.py`（重写：7 条件 + 接收 `ResearchState`）
  - `agents/explanation_agent.py`（小幅调整：接收 `ResearchState`，保留 `_rule_explain` 离线回退）
  - `agents/hypothesis_agent.py`（小幅调整：接收 `ResearchState`，保留 `_default_hypothesis` 离线回退）
  - `agents/decision_agent.py`（小幅调整：新增 `select_best_from_state(state)`，兼容旧 `select_best(env, scored)`）
  - `agents/evaluation_agent.py` / `rule_agent.py` / `knowledge_agent.py` / `literature_agent.py` / `fact_extraction_agent.py` / `parameter_agent.py` / `environment_agent.py` / `data_agent.py`（新增 `*_from_state` 风格入口，保留旧方法）
  - `map/map_analyzer.py`（扩展 `analyze` 字段）
  - `llm/prompt_templates.py`（新增 `REFLECTION_SYSTEM_PROMPT` / `REFLECTION_USER_TEMPLATE`）
  - `agents/__init__.py`（导出新增类）

## ADDED Requirements

### Requirement: 统一状态对象 ResearchState

`agents/research_state.py` SHALL 提供 `ResearchState` dataclass，要求：

1. 字段 SHALL 至少包含：`env_input: dict`、`map_features: dict = None`、`literature_facts: list = None`、`algorithm_records: list = None`、`scored_algorithms: list = None`、`decision: dict = None`、`recommended_params: dict = None`、`hypothesis: dict = None`、`experiment_results: list = None`、`reflection: dict = None`、`report: str = None`、`metadata: dict = None`。
2. SHALL 提供 `to_dict() -> dict` 与 `@staticmethod from_dict(d: dict) -> "ResearchState"` 序列化方法。
3. SHALL 提供 `summary() -> str` 方法，返回关键字段的摘要字符串，至少包含：`scene_level`（从 `decision` / `metadata` 推断）、`best_algorithm`、`best_score`、`need_human_check`、`map_features` 中的关键键（`cluster_count` / `bottleneck_count` / `entropy` / `distance_to_target`），以及 `errors` / `human_check_reasons` 数量。
4. 构造时 SHALL 自动初始化 `metadata = {"created_at": <ISO-8601>, "pipeline_version": "phase-4"}`。

#### Scenario: ResearchState 基础摘要
- **WHEN** 执行 `python -c "from agents.research_state import ResearchState; rs=ResearchState(env_input={'test':True}); print(rs.summary())"`
- **THEN** SHALL 输出非空摘要字符串

#### Scenario: to_dict / from_dict 往返一致
- **WHEN** 对 `ResearchState(env_input={'a':1}, map_features={'b':2})` 调 `to_dict()` 后再 `from_dict()`
- **THEN** 恢复得到的对象 SHALL 与原对象字段相等

### Requirement: MapAnalysisAgent 地图结构分析

`agents/map_analysis_agent.py` SHALL 提供 `MapAnalysisAgent` 类，要求：

1. `analyze_grid(grid: np.ndarray) -> dict` 方法 SHALL 计算：
   - `cluster_count`：障碍物 `1` 的连通区域数量（4 邻接，`scipy.ndimage.label` 或自实现 BFS）；
   - `largest_free_ratio`：最大可通行 `0` 连通区域占比；
   - `bottleneck_count`：宽度 < 3 的必经通道数量（在自由空间骨架上做"中间度"或"窄通道"近似）；
   - `entropy`：障碍物空间分布熵（按行/列分段统计 0/1 分布后求 Shannon 熵或简化熵）。
2. `extract_features(grid, start, target) -> dict` 方法 SHALL 整合：
   - `MapAnalyzer.analyze(grid, start, target)` 的输出；
   - `analyze_grid` 的四个字段；
   - `distance_to_target`：`abs(start[0]-target[0]) + abs(start[1]-target[1])`。
3. `MapAnalysisAgent.analyze(state: ResearchState)` SHALL 接收 `ResearchState`，从 `state.env_input` / `state.map_features["grid"]` 读取输入，并把结果写入 `state.map_features`，最后返回 `state`。
4. `map/map_analyzer.py` 的 `MapAnalyzer.analyze` SHALL 新增字段 `cluster_count` / `bottleneck_count` / `entropy` / `distance_to_target`，缺失底层实现时 SHALL 提供"占位计算"（如 `cluster_count=0`、`bottleneck_count=0`、`entropy=0.0`）以保证不抛错。

#### Scenario: 零障碍物网格
- **WHEN** 执行 `python -c "from agents.map_analysis_agent import MapAnalysisAgent; import numpy as np; ma=MapAnalysisAgent(); f=ma.extract_features(np.zeros((20,20),dtype=np.int8),(0,0),(19,19)); print('bottleneck_count' in f)"`
- **THEN** SHALL 输出 `True`

#### Scenario: ResearchState 集成
- **WHEN** 调用 `MapAnalysisAgent().analyze(state)` 且 `state.env_input` 中包含 `map_filepath` 或 `map_features["grid"]`
- **THEN** `state.map_features` SHALL 至少包含 `cluster_count` / `bottleneck_count` / `entropy` / `distance_to_target` 四个键

### Requirement: Orchestrator 12 智能体流水线

`agents/orchestrator_agent.py` 的 `OrchestratorAgent` SHALL 升级，要求：

1. `__init__(self, use_qwen: bool = False)` SHALL 实例化下列智能体并存为实例属性：`self.data_agent = DataReceiverAgent()`、`self.map_agent = MapAnalysisAgent()`、`self.env_agent = EnvironmentAgent()`、`self.literature_agent = LiteratureAgent()`、`self.fact_agent = FactExtractionAgent(use_qwen=use_qwen)`、`self.knowledge_agent = KnowledgeRetrievalAgent()`、`self.rule_agent = RuleConstraintAgent()`、`self.eval_agent = AlgorithmEvaluationAgent()`、`self.parameter_agent = ParameterAgent()`、`self.decision_agent = DecisionAgent()`、`self.human_agent = HumanLoopAgent()`、`self.explanation_agent = ExplanationAgent(use_qwen=use_qwen)`、`self.hypothesis_agent = HypothesisAgent(use_qwen=use_qwen)`、`self.reflection_agent = ReflectionAgent(use_qwen=use_qwen)`。
2. `run(self, env_input: dict) -> ResearchState` SHALL 按以下顺序逐级写入 `ResearchState`（每步失败 SHALL 把异常追加到 `state.metadata["errors"]` 并不中断后续步骤）：
   1. `state = self.data_agent.validate_state(env_input)`（写入 `state.env_input` 与 `state.metadata` 中的 `validated` 信息）；
   2. `state = self.map_agent.analyze(state)`；
   3. `state = self.env_agent.classify_state(state)`（写入 `state.decision["scene_level"]` 前的中间字段到 `state.metadata["scene_level"]`）；
   4. `state = self.literature_agent.enrich_state(state)`、`state = self.fact_agent.enrich_state(state)`；
   5. `state = self.knowledge_agent.retrieve_state(state)`；
   6. `state = self.rule_agent.filter_and_penalize_state(state)`；
   7. `state = self.eval_agent.score_state(state)`；
   8. `state = self.decision_agent.select_best_state(state)`；
   9. `state = self.human_agent.check(state)`；
   10. `state = self.explanation_agent.explain_state(state)`；
   11. `state = self.hypothesis_agent.generate_state(state)`；
   12. `state = self.reflection_agent.reflect(state)`；
   13. `state.recommended_params = self.parameter_agent.recommend(state.env_input, state.decision or {})`。
3. 每个智能体 SHALL 同时保留旧接口（接收 `env` 字典 / 返回 `env` 字典），并新增 `*_state(state)` 入口，**新增入口不破坏旧调用方**。
4. `main.py` 现有 `PathPlanningDecisionSystem.decide` SHALL 保持不变（继续返回 `decision` 字典），不强制改造为 `ResearchState`，避免破坏 Phase 0 / Phase 1 既有测试。

#### Scenario: 手工输入运行成功
- **WHEN** 执行 `python -c "from agents.orchestrator_agent import OrchestratorAgent; o=OrchestratorAgent(); result=o.run({'obstacle_ratio':0.35,'map_width':100,'map_height':100,'connectivity':0.68,'topology_randomness':0.55,'compute_limit':'medium'}); print(type(result).__name__)"`
- **THEN** SHALL 输出 `ResearchState`

#### Scenario: main.py 兼容
- **WHEN** 执行 `python main.py`
- **THEN** SHALL 不报错（输出 3 组场景的排名详情）

#### Scenario: 中间步骤失败不中断
- **WHEN** `LiteratureAgent.enrich_state` 抛出异常（例如文献知识库损坏）
- **THEN** `state.metadata["errors"]` SHALL 包含对应错误信息，且后续智能体 SHALL 继续运行

### Requirement: HumanLoopAgent 7 条件触发

`agents/human_loop_agent.py` 的 `HumanLoopAgent.check` SHALL 接收 `ResearchState`，要求：

1. 触发条件 1：前两名 `scored_algorithms` 得分差 < `SCORE_GAP_THRESHOLD`（保留原行为）；
2. 触发条件 2：知识库中 `state.algorithm_records` 为空列表，或场景等级未命中知识库（`scene_level` 缺失对应记录）；
3. 触发条件 3：推荐算法 (`state.decision["best_algorithm"]`) 与 `state.algorithm_records` 中按"成功率"或"综合得分"最高者不一致，且不一致差距 > 一定阈值；
4. 触发条件 4：场景等级为"高复杂度"且所有算法 `success_rate < 0.5`；
5. 触发条件 5：`state.env_input["user_preference"]` 存在于 `{"safety_first", "time_first", "success_first"}`（即用户指定了权重偏好）；
6. 触发条件 6：`len(state.literature_facts or []) < 2`；
7. 触发条件 7：引用的文献中存在 `verified == False` 的条目（通过 `state.literature_facts` 中 `verified` 字段判断）。
8. 每命中一条 SHALL 把具体原因（中文）追加到 `state.metadata["human_check_reasons"]` 列表；只要列表非空，SHALL 同步将 `state.decision["need_human_check"] = True`；否则保持 `False`。
9. 旧接口 `check(decision: dict) -> dict` SHALL 保留（兼容旧调用方），其内部 SHALL 委托到 `check_state` 或保留原 1 条件判断。

#### Scenario: 边界输入触发
- **WHEN** 构造 `state.algorithm_records = [{"algorithm": "A*", "score": 0.80, "success_rate": 0.7}, {"algorithm": "ACO", "score": 0.78, "success_rate": 0.6}]`、`state.decision = {"best_algorithm": "A*", "ranking": []}` 且 `scene_level = "高复杂度"`
- **THEN** `state.metadata["human_check_reasons"]` SHALL 至少包含"前两名得分差距过小"和"高复杂度下所有算法成功率 < 0.5"两条

#### Scenario: 既有测试不破坏
- **WHEN** 执行 `python -m pytest tests/test_decision_agent.py -v`
- **THEN** SHALL 全部通过（`test_decision_agent.py` 不依赖 `HumanLoopAgent`，应无回归）

### Requirement: ReflectionAgent 决策反思

`agents/reflection_agent.py` SHALL 提供 `ReflectionAgent` 类，要求：

1. `__init__(self, qwen_client=None, use_qwen: bool = True)` SHALL 接收可选 `QwenClient`；`use_qwen=False` 时 SHALL 走离线 `_rule_reflect` 路径，不实例化 QwenClient。
2. `reflect(self, state: ResearchState) -> ResearchState` SHALL 执行 7 项反思检查：
   - 推荐算法是否真的是实验最优（核对 `state.decision` 与 `state.algorithm_records` 一致性）；
   - 是否存在另一个算法成功率更高（`success_rate` 排序）；
   - 是否只是耗时最短但成功率不足（`avg_time` 最短者 `success_rate` 是否偏低）；
   - 文献依据是否真实（`state.literature_facts` 是否有 `verified == False` 或空）；
   - 数据是否覆盖低/中/高复杂度（`state.algorithm_records` 中 `scene_level` 分布）；
   - 实验次数是否足够（≥ 3 次/算法，可由 `experiment_results` 推断，若无则视为"信息不足"）；
   - 结论是否过度泛化（`state.decision` 中 `best_algorithm` 与 `scene_level` 是否强绑定且无对照组）。
3. 输出 SHALL 为 dict `{"confidence_score": float (0~1), "issues": list[str], "suggestions": list[str], "passed": bool}`，并存入 `state.metadata["reflection"]`。
4. `_rule_reflect(state)` SHALL 提供纯规则离线版本：默认 `confidence_score = 0.6`，无明显问题则 `passed = True`，命中"高复杂度全部算法成功率 < 0.5"或"知识库空"等硬伤时 `passed = False` 且 `confidence_score` ≤ 0.4。
5. `llm/prompt_templates.py` SHALL 新增 `REFLECTION_SYSTEM_PROMPT`（声明角色为"路径规划 AI Scientist 反思者"）与 `REFLECTION_USER_TEMPLATE`（含 `state` 关键字段占位符）。

#### Scenario: 离线反思输出
- **WHEN** 执行 `python -c "from agents.reflection_agent import ReflectionAgent; ra=ReflectionAgent(use_qwen=False); from agents.research_state import ResearchState; rs=ResearchState(env_input={'test':True}); rs.decision={'best_algorithm':'A*','scene_level':'高复杂度','ranking':[]}; result=ra.reflect(rs); print(result.metadata.get('reflection'))"`
- **THEN** SHALL 输出非空反思结果 dict（包含 `confidence_score` / `issues` / `suggestions` / `passed`）

#### Scenario: 知识库空触发失败标记
- **WHEN** `state.algorithm_records = []` 且 `use_qwen=False`
- **THEN** `result.metadata["reflection"]["passed"]` SHALL 为 `False`，且 `issues` SHALL 包含类似"知识库为空"的中文描述

## MODIFIED Requirements

### Requirement: 智能体旧接口保持兼容（来自 Phase 0 / Phase 1）

`agents/data_agent.py`、`agents/environment_agent.py`、`agents/knowledge_agent.py`、`agents/rule_agent.py`、`agents/evaluation_agent.py`、`agents/decision_agent.py`、`agents/explanation_agent.py`、`agents/hypothesis_agent.py`、`agents/human_loop_agent.py`、`agents/parameter_agent.py` 的**既有方法签名** SHALL 保持不变。本阶段 SHALL 在这些智能体上**追加** `*_state(state)` 系列入口（接收 `ResearchState`、返回 `ResearchState`），但**不修改或删除**既有 `validate` / `classify` / `retrieve` / `filter_and_penalize` / `score` / `select_best` / `explain` / `generate` / `check` / `recommend` 等方法，以确保 `main.py` 既有调用与 `tests/test_decision_agent.py` 等测试不被破坏。

### Requirement: MapAnalyzer.analyze 字段扩展（提示词 4-2 衍生）

`map/map_analyzer.py` 的 `MapAnalyzer.analyze` SHALL **保留**既有的 `scene_level` / `complexity_index` / `obstacle_ratio` / `start` / `target` / `free_space_ratio` / `total_cells` 7 个字段，**追加** `cluster_count` / `bottleneck_count` / `entropy` / `distance_to_target` 4 个字段（缺失底层实现时返回占位值 0 / 0 / 0.0 / `abs(start[0]-target[0]) + abs(start[1]-target[1])`），以避免破坏现有调用方对返回结构的既有假设。

## REMOVED Requirements

无。
