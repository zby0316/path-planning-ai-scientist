# Checklist（Phase 5 假设生成—实验验证闭环）

> 验证方法：每个条目在实现完成后由 Sub-Agent 或主流程实际执行/审阅，并通过在条目开头勾选 `[x]` 标记通过。

## HypothesisAgent 4 段结构化假设（提示词 5-1）

- [x] `llm/prompt_templates.py` 末尾追加 `HYPOTHESIS_SYSTEM_PROMPT_V2` 与 `HYPOTHESIS_USER_TEMPLATE_V2`
- [x] `HYPOTHESIS_SYSTEM_PROMPT_V2` 声明 4 段 JSON 结构：`hypothesis_text` / `experiment_plan` / `expected_results` / `boundary_conditions`
- [x] `hypothesis_text` 模板要求"在 X 条件下，算法 Y 相比 Z 在指标 W 上有显著优势"句式
- [x] `experiment_plan` 至少含 `maps` / `algorithms` / `runs_per_algorithm` / `metrics` 4 字段
- [x] `expected_results` 至少含 `best_algorithm` / `success_rate_threshold` / `time_budget_seconds` 3 字段
- [x] `boundary_conditions` 为数组，每项一句中文
- [x] `HypothesisAgent.generate(state: ResearchState) -> ResearchState` 新入口存在（通过 `*args` 分派实现）
- [x] LLM 返回非 JSON 时回退到 `_default_hypothesis_struct(state)`，异常追加到 `state.metadata["errors"]`
- [x] `_default_hypothesis_struct(state)` 返回 4 段结构化 dict
- [x] `_default_hypothesis(env, decision)` 升级为 10 字段字符串（待研究问题 / 科学假设 / 解决思路 / 必要技术手段 / 数据集 / 论文标题 / 摘要 / 方法论 / 实验设计 / 参考论文）
- [x] 旧 `generate(env, decision, explanation) -> str` 签名保留
- [x] 旧 `generate_state(state) -> ResearchState` 签名保留
- [x] 4 段结构对象最终形态包含 `hypothesis_text` / `experiment_plan` / `expected_results` / `boundary_conditions` / `raw_text` / `generated_by`
- [x] 离线模式执行 `python -c "...hypothesis_text' in rs.hypothesis..."` 输出 `True`
- [x] `hypothesis_text` / `experiment_plan` / `expected_results` / `boundary_conditions` 4 个键在 `state.hypothesis` 中同时存在

## ExperimentAgent 自动实验验证（提示词 5-2）

- [x] `agents/experiment_agent.py` 存在并实现 `ExperimentAgent` 类
- [x] `__init__(db, benchmark_runner)` 接收 `ExperimentDB` 与 `BenchmarkRunner` 实例
- [x] `_default_experiment_plan(state)` 返回 `maps.count=50` / `width=100` / `height=100` / 5 算法 / `runs_per_algorithm=5`
- [x] `run_validation(state)` 读取 `state.hypothesis["experiment_plan"]`，缺失回退默认
- [x] 使用 `MapGenerator` 生成对应复杂度与规模的随机地图（默认 50 张）
- [x] 每张地图调 `BenchmarkRunner.run(grid, start, target, n_runs=5)` 跑 5 算法
- [x] 逐条结果调 `ExperimentDB.insert_run` 写入 `data/experiments/experiments.sqlite`
- [x] 按算法聚合 `success_rate` / `avg_runtime` / `avg_path_length` / `stability_score` 写入 `state.experiment_results`
- [x] `compare_with_hypothesis(state)` 返回布尔值
- [x] 判定规则：推荐算法 `success_rate > 次优 10%` 且 `len(experiment_results) >= 2` → `True`
- [x] `state.metadata["hypothesis_supported"]` 与 `state.metadata["hypothesis_support_score"]` 写入
- [x] `state.metadata["hypothesis_support_details"]` 写入（5 字段诊断信息）
- [x] 中途异常追加到 `state.metadata["errors"]`，不中断流水线
- [x] `state.experiment_results` 每条至少含 `algorithm` / `n_maps` / `success_rate` / `avg_runtime` / `avg_path_length` / `stability_score`
- [x] 冒烟测试 `len(rs.experiment_results) >= 2` 与 `rs.metadata["hypothesis_supported"] in (True, False)` 通过（实测 `n_results=5`, `hypothesis_supported=False`）
- [x] 假设不支持场景：`expected_results.best_algorithm="A*"` 且 ACO 成功率 > A* → `hypothesis_supported == False`

## ScientificDiscoveryPipeline 闭环（提示词 5-3）

- [x] `agents/pipeline.py` 存在并实现 `ScientificDiscoveryPipeline` 类
- [x] `__init__(use_qwen=False)` 实例化 `OrchestratorAgent` / `HypothesisAgent` / `ExperimentAgent` / `ReflectionAgent`
- [x] `run_full_cycle(env_input, max_iterations=3)` 串联 orchestrator → hypothesis → experiment → reflection
- [x] 迭代循环正确执行（iteration 从 1 开始，≤ max_iterations）
- [x] `confidence_score >= 0.7` 或达到 `max_iterations` 时退出循环
- [x] 每次迭代记录到 `state.metadata["iterations"]` 列表
- [x] 每条 iteration dict 至少含 `iteration` / `hypothesis_summary` / `hypothesis_supported` / `confidence_score` / `issues`
- [x] 假设修正逻辑：`confidence_score < 0.7` 且未到 `max_iterations` 时把 `reflection.issues` 注入 `state.metadata["hypothesis_revisions"]`
- [x] `export_report(state, filepath)` 调 `ReportGenerator(state).save_to_file(filepath)`，默认 `config.REPORTS_DIR`
- [x] 执行 `python -c "from agents.pipeline import ScientificDiscoveryPipeline; ..."` 输出至少 1 个迭代 dict（实测 `iterations count: 1`，5 个必需键齐全）
- [x] `max_iterations=2` 且第 1 次 `confidence_score < 0.7` 时 `len(state.metadata["iterations"]) == 2`
- [x] **循环导入已修复**：`from reports.report_generator import ReportGenerator` 已挪进 `export_report` 方法体内（延迟导入），打断 `agents → pipeline → reports` 与 `reports → agents` 的环；修复后 `from reports.report_generator import ReportGenerator` 与 `from agents import ...` 同时可导入

## ReportGenerator 标准化 10 字段报告（提示词 5-4）

- [x] `reports/__init__.py` 存在并导出 `ReportGenerator`
- [x] `reports/report_generator.py` 存在并实现 `ReportGenerator` 类
- [x] `__init__(state: ResearchState)` 保存 `state` 到 `self.state`
- [x] `generate()` 输出包含 10 个固定顺序二级标题：`## 1. 待研究问题 Problem Statement` ... `## 10. 参考论文 References`
- [x] 字段 1 / 2 / 3 / 5 / 6 / 7 来源于 `state.hypothesis["hypothesis_text"]` 与 `state.hypothesis["raw_text"]`
- [x] 字段 4 数据集来源于 `state.env_input` 与 `state.map_features`
- [x] 字段 8 实验设计来源于 `state.hypothesis["experiment_plan"]` 与 `state.recommended_params`
- [x] 字段 9 实验结果来源于 `state.experiment_results` 与 `state.metadata.get("hypothesis_supported")`
- [x] 字段 10 参考论文来源于 `state.literature_facts`，并经过 `CitationAgent(check_doi_online=False).validate_references()` 过滤为 `valid`
- [x] 网络不可用时全部纳入并标注 `verification_pending: true`
- [x] 报告末尾追加生成时间戳（ISO-8601）与系统版本（`pipeline_version`）
- [x] `save_to_file(filepath)` 默认目录 `config.REPORTS_DIR`（即 `reports/generated_reports/`）
- [x] 自动 `os.makedirs(..., exist_ok=True)` 创建父目录
- [x] 返回最终写入文件的绝对路径
- [x] 执行最小冒烟：`reports/generated_reports/` 下生成 `.md` 文件（实测 `PATH: D:\...\reports\generated_reports\report_2026-06-09T10-41-02Z.md`）
- [x] 打开文件确认 10 个二级标题且顺序正确（实测 `OK: 10 个二级标题齐全`）
- [x] 离线模式下 `validate_references` 不会发起网络请求（`check_doi_online=False`）

## 模块导出（提示词 5-1 ~ 5-4）

- [x] `agents/__init__.py` 导出 `ExperimentAgent`
- [x] `agents/__init__.py` 导出 `ScientificDiscoveryPipeline`
- [x] `python -c "from agents import ExperimentAgent, ScientificDiscoveryPipeline, HypothesisAgent, ResearchState; print('imports OK')"` 输出 `imports OK`
- [x] `python -c "from reports.report_generator import ReportGenerator; print('imports OK')"` 输出 `imports OK`（循环导入修复后）

## 整体收口

- [x] Phase 0 / Phase 1 / Phase 4 既有所有验证命令全部通过（`python main.py` 正常运行，3 组场景输出排名详情；`python -c "import config; print('config OK')"` 通过）
- [x] `python -m pytest tests/ -v` 既有测试全部通过（**21/21**：`test_astar.py` 2 + `test_decision_agent.py` 3 + `test_environment_agent.py` 6 + `test_integration.py` 3 + `test_map_generator.py` 1 + `test_scoring.py` 6）
- [x] `HypothesisAgent.generate(env, decision, explanation)` 旧签名保留，调用方不被破坏（实测 `legacy generate returns str: True`）
- [x] `HypothesisAgent.generate_state(state)` 旧入口保留
- [x] `llm/prompt_templates.py` 旧 `HYPOTHESIS_SYSTEM_PROMPT` / `HYPOTHESIS_USER_TEMPLATE` 同时保留（V1 / V2 共存，4 个常量全部存在）
- [x] `agents/orchestrator_agent.py` 12+ 智能体流水线行为不被破坏（`OrchestratorAgent().run()` 仍返回 `ResearchState`）
- [x] `reports/` 目录在仓库根目录下被创建（`reports/__init__.py` + `reports/report_generator.py` + `reports/generated_reports/report_*.md`）
- [x] 实现阶段所有 Sub-Agent 任务均按 tasks.md 执行完毕
