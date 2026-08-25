# Tasks

> 范围：Phase 4 多智能体协同升级，对应提示词 4-1 ~ 4-5。
> 实现阶段需先阅读 `.trae/specs/phase-4-multi-agent-orchestration/spec.md`。

- [x] Task 1（提示词 4-1）：新建 `agents/research_state.py` 实现 `ResearchState`
  - [x] SubTask 1.1：定义 `@dataclass class ResearchState`，至少包含 12 个字段（`env_input` / `map_features` / `literature_facts` / `algorithm_records` / `scored_algorithms` / `decision` / `recommended_params` / `hypothesis` / `experiment_results` / `reflection` / `report` / `metadata`），`__post_init__` 自动初始化 `metadata = {"created_at": <ISO-8601>, "pipeline_version": "phase-4"}`
  - [x] SubTask 1.2：实现 `to_dict()` / `from_dict(d)` 序列化方法
  - [x] SubTask 1.3：实现 `summary()` 方法，至少输出 `scene_level` / `best_algorithm` / `best_score` / `need_human_check` / `cluster_count` / `bottleneck_count` / `entropy` / `distance_to_target` / `errors_count` / `human_check_reasons_count`
  - [x] SubTask 1.4：执行 `python -c "from agents.research_state import ResearchState; rs=ResearchState(env_input={'test':True}); print(rs.summary())"` 验证输出非空

- [x] Task 2（提示词 4-2）：新建 `agents/map_analysis_agent.py` 实现 `MapAnalysisAgent` + 扩展 `MapAnalyzer.analyze`
  - [x] SubTask 2.1：在 `map/map_analyzer.py` 的 `MapAnalyzer.analyze` 既有 7 字段上**追加** `cluster_count` / `bottleneck_count` / `entropy` / `distance_to_target`，缺失底层实现时使用占位值（0 / 0 / 0.0 / Manhattan 距离）
  - [x] SubTask 2.2：实现 `MapAnalysisAgent.analyze_grid(grid)` 方法，使用 `scipy.ndimage.label`（如可用）或自实现 BFS 计算 `cluster_count` / `largest_free_ratio` / `bottleneck_count` / `entropy`（依赖缺失时全部降级为 0）
  - [x] SubTask 2.3：实现 `MapAnalysisAgent.extract_features(grid, start, target)` 方法，整合 `MapAnalyzer.analyze` 与 `analyze_grid` 的所有字段
  - [x] SubTask 2.4：实现 `MapAnalysisAgent.analyze(state: ResearchState)` 方法：若 `state.map_features` 中含 `grid` 则基于栅格分析；否则读 `state.env_input["map_filepath"]` 经 `MapParser().parse()` 得到栅格；最终结果合并到 `state.map_features`，返回 `state`
  - [x] SubTask 2.5：执行 `python -c "from agents.map_analysis_agent import MapAnalysisAgent; import numpy as np; ma=MapAnalysisAgent(); f=ma.extract_features(np.zeros((20,20),dtype=np.int8),(0,0),(19,19)); print('bottleneck_count' in f)"` 验证输出 `True`
  - [x] SubTask 2.6：执行 `python -c "from agents.map_analysis_agent import MapAnalysisAgent; from agents.research_state import ResearchState; s=ResearchState(env_input={'test':True}); s.map_features={'grid':[[0,0],[0,0]]}; s=MapAnalysisAgent().analyze(s); print('entropy' in s.map_features)"` 验证 `entropy` 键存在

- [x] Task 3（提示词 4-3）：升级 `agents/orchestrator_agent.py` 为 12 智能体流水线
  - [x] SubTask 3.1：在 `__init__` 中实例化全部 14 个智能体属性（`data_agent` / `map_agent` / `env_agent` / `literature_agent` / `fact_agent` / `knowledge_agent` / `rule_agent` / `eval_agent` / `parameter_agent` / `decision_agent` / `human_agent` / `explanation_agent` / `hypothesis_agent` / `reflection_agent`）
  - [x] SubTask 3.2：实现 `run(env_input) -> ResearchState` 主流程，按 spec 顺序调用 12 个步骤；每步用 try/except 包裹，失败时把异常追加到 `state.metadata["errors"]` 并继续
  - [x] SubTask 3.3：给现有 `data_agent` / `env_agent` / `knowledge_agent` / `rule_agent` / `eval_agent` / `decision_agent` / `explanation_agent` / `hypothesis_agent` 追加 `*_state(state)` 入口，**不修改**其旧方法签名
  - [x] SubTask 3.4：给 `literature_agent` / `fact_extraction_agent` 追加 `enrich_state(state)` 入口
  - [x] SubTask 3.5：执行 `python -c "from agents.orchestrator_agent import OrchestratorAgent; o=OrchestratorAgent(); result=o.run({'obstacle_ratio':0.35,'map_width':100,'map_height':100,'connectivity':0.68,'topology_randomness':0.55,'compute_limit':'medium'}); print(type(result).__name__)"` 验证输出 `ResearchState`
  - [x] SubTask 3.6：执行 `python main.py` 验证旧 `PathPlanningDecisionSystem.decide` 仍正常运行
  - [x] SubTask 3.7：执行 `python -m pytest tests/ -v` 验证既有测试不回归

- [x] Task 4（提示词 4-4）：升级 `agents/human_loop_agent.py` 触发条件至 7 种
  - [x] SubTask 4.1：保留旧接口 `check(decision: dict) -> dict`（1 条件 SCORE_GAP），**不删除**
  - [x] SubTask 4.2：实现新接口 `check_state(state: ResearchState) -> ResearchState`，依次检查 7 种触发条件
  - [x] SubTask 4.3：把 `check` 改为薄包装：检测到 `state` 类型（`ResearchState`）时委托到 `check_state`，否则走旧路径
  - [x] SubTask 4.4：构造边界输入（`algorithm_records` 空、`success_rate < 0.5`、`user_preference`、`literature_facts` 长度不足、`verified == False` 等）验证至少 4 种条件能命中
  - [x] SubTask 4.5：执行 `python -m pytest tests/test_decision_agent.py -v` 确认既有测试不受影响

- [x] Task 5（提示词 4-5）：新建 `agents/reflection_agent.py` 实现 `ReflectionAgent` + 反思 Prompt
  - [x] SubTask 5.1：在 `llm/prompt_templates.py` 末尾追加 `REFLECTION_SYSTEM_PROMPT` 与 `REFLECTION_USER_TEMPLATE`（含 `state_summary` / `decision` / `records` / `literature_facts` 等占位符）
  - [x] SubTask 5.2：实现 `ReflectionAgent.__init__(qwen_client=None, use_qwen=True)`，仅当 `use_qwen=True` 且 `qwen_client` 提供时才实例化 QwenClient
  - [x] SubTask 5.3：实现 `reflect(state)` 方法：先调用 `_qwen_reflect` 或 `_rule_reflect` 生成 7 项反思结果，存入 `state.metadata["reflection"]`，并把 `confidence_score` / `issues` / `suggestions` / `passed` 同步到 `state.reflection`
  - [x] SubTask 5.4：实现 `_rule_reflect(state)` 离线回退：默认 `confidence_score=0.6` / `passed=True`；命中硬伤（知识库空 / 高复杂度全部算法 `success_rate<0.5` / 文献全 `verified==False`）时 `passed=False`、`confidence_score<=0.4` 并追加 issues
  - [x] SubTask 5.5：执行 `python -c "from agents.reflection_agent import ReflectionAgent; ra=ReflectionAgent(use_qwen=False); from agents.research_state import ResearchState; rs=ResearchState(env_input={'test':True}); rs.decision={'best_algorithm':'A*','scene_level':'高复杂度','ranking':[]}; result=ra.reflect(rs); print(result.metadata.get('reflection'))"` 验证输出非空反思 dict

- [x] Task 6（提示词 4-1 ~ 4-5）：更新 `agents/__init__.py` 导出
  - [x] SubTask 6.1：从 `agents.research_state` 导出 `ResearchState`
  - [x] SubTask 6.2：从 `agents.map_analysis_agent` 导出 `MapAnalysisAgent`
  - [x] SubTask 6.3：从 `agents.reflection_agent` 导出 `ReflectionAgent`
  - [x] SubTask 6.4：执行 `python -c "from agents import ResearchState, MapAnalysisAgent, ReflectionAgent, OrchestratorAgent, HumanLoopAgent; print('imports OK')"` 验证全部可导入

# Task Dependencies

- Task 1（ResearchState）独立，可最先开始；Task 2 / Task 3 / Task 4 / Task 5 全部依赖 Task 1（需 `ResearchState` 作为入参/出参）
- Task 2（MapAnalysisAgent + MapAnalyzer 扩展）依赖 Task 1，独立于 Task 4 / Task 5
- Task 4（HumanLoopAgent 7 条件）依赖 Task 1；可与 Task 2 / Task 5 并行
- Task 5（ReflectionAgent）依赖 Task 1；可与 Task 2 / Task 4 并行
- Task 3（Orchestrator 12 智能体流水线）依赖 Task 1、Task 2（需 `MapAnalysisAgent`）、Task 4（需 `HumanLoopAgent.check_state`）、Task 5（需 `ReflectionAgent.reflect`）
- Task 6（模块导出）依赖 Task 1 ~ Task 5 全部完成
- 整体收口（验证命令）依赖 Task 1 ~ Task 6 全部完成
