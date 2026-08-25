# Tasks

> 范围：Phase 5 假设生成—实验验证闭环，对应提示词 5-1 ~ 5-4。
> 实现阶段需先阅读 `.trae/specs/phase-5-hypothesis-experiment-loop/spec.md`。

- [x] Task 1（提示词 5-1）：升级 `agents/hypothesis_agent.py` 为 4 段结构化假设
  - [x] SubTask 1.1：在 `llm/prompt_templates.py` 末尾追加 `HYPOTHESIS_SYSTEM_PROMPT_V2`（声明 4 段 JSON 结构和 4 个键 `hypothesis_text` / `experiment_plan` / `expected_results` / `boundary_conditions`）与 `HYPOTHESIS_USER_TEMPLATE_V2`（含 `best_algorithm` / `scene_level` / `ranking` / `env_detail` 占位符）
  - [x] SubTask 1.2：在 `HypothesisAgent` 中新增 `generate(self, state: ResearchState) -> ResearchState` 入口：调用 `QwenClient.chat(SYSTEM_V2, USER_V2.format(...))` 拿到文本，正则提取 JSON 段（`re.search(r"\{.*\}"s, text, re.DOTALL)`），解析失败时回退到 `_default_hypothesis_struct(state)` 并把异常追加到 `state.metadata["errors"]`
  - [x] SubTask 1.3：实现 `_default_hypothesis_struct(state)` 离线规则生成器：返回 4 段结构化 dict，包含 `hypothesis_text` / `experiment_plan` / `expected_results` / `boundary_conditions` / `raw_text` / `generated_by`，字段值基于 `state.env_input` / `state.decision` / `state.literature_facts` / `state.algorithm_records` 填充
  - [x] SubTask 1.4：升级 `_default_hypothesis(self, env, decision)` 为 10 字段模板字符串：待研究问题 / 科学假设 / 解决思路 / 必要技术手段 / 数据集 / 论文标题 / 摘要 / 方法论 / 实验设计 / 参考论文
  - [x] SubTask 1.5：保留旧 `generate(self, env, decision, explanation) -> str` 与 `generate_state(self, state) -> ResearchState` 签名，**不删除不修改**，并在 `generate_state` 中委托到新的 `generate(state)` 入口
  - [x] SubTask 1.6：执行
    ```bash
    python -c "from agents.hypothesis_agent import HypothesisAgent; \
    ha=HypothesisAgent(use_qwen=False); \
    from agents.research_state import ResearchState; \
    rs=ResearchState(env_input={'obstacle_ratio':0.65,'connectivity':0.3}); \
    rs.decision={'best_algorithm':'混合优化算法','scene_level':'高复杂度','ranking':[],'best_score':0.85}; \
    h=ha.generate(rs); print('hypothesis_text' in rs.hypothesis)"
    ```
    验证输出 `True` ✓

- [x] Task 2（提示词 5-2）：新建 `agents/experiment_agent.py` 实现 `ExperimentAgent`
  - [x] SubTask 2.1：定义 `class ExperimentAgent`，`__init__(self, db: ExperimentDB, benchmark_runner: BenchmarkRunner)` 接收 `ExperimentDB`（`data/experiment_db.py`）与 `BenchmarkRunner`（`evaluation/benchmark.py`）实例
  - [x] SubTask 2.2：实现 `_default_experiment_plan(state)` 返回 `{"maps": {"count": 50, "width": 100, "height": 100, "obstacle_ratio": <from env>}, "algorithms": ["A*","ACO","PSO","SA","混合优化算法"], "runs_per_algorithm": 5, "metrics": ["success_rate","avg_time","avg_path_length","stability_score"]}`
  - [x] SubTask 2.3：实现 `run_validation(self, state) -> ResearchState`：从 `state.hypothesis["experiment_plan"]` 读取（缺失回退默认）；用 `MapGenerator(seed=...)` 生成 N 张地图；对每张地图调 `BenchmarkRunner.run(grid, start, target, n_runs=5)` 拿到 5 算法结果；逐条调 `ExperimentDB.insert_run` 写入 SQLite；按算法聚合 `success_rate` / `avg_runtime` / `avg_path_length` / `stability_score` 写入 `state.experiment_results`（list of dict）
  - [x] SubTask 2.4：实现 `compare_with_hypothesis(self, state) -> bool`：计算推荐算法 vs 次优算法的 `success_rate` 差值；满足"推荐算法 > 次优 10% 且 len(experiment_results) >= 2"返回 `True`，否则 `False`；同时把布尔值与连续分写入 `state.metadata["hypothesis_supported"]` / `state.metadata["hypothesis_support_score"]`
  - [x] SubTask 2.5：在 `run_validation` 中用 `try/except` 包裹每张地图生成与每条 `insert_run` 调用，失败时把异常追加到 `state.metadata["errors"]` 并继续（不中断流水线）
  - [x] SubTask 2.6：执行最小冒烟（3 张地图 × 5 算法）：
    ```python
    ea = ExperimentAgent(db=ExperimentDB(), benchmark_runner=BenchmarkRunner())
    rs = ea.run_validation(rs)
    ```
    验证 `len(rs.experiment_results) == 5` 与 `rs.metadata["hypothesis_supported"] in (True, False)` ✓ 实际输出 `n_results=5`, `hypothesis_supported=False`

- [x] Task 3（提示词 5-3）：新建 `agents/pipeline.py` 实现 `ScientificDiscoveryPipeline`
  - [x] SubTask 3.1：定义 `class ScientificDiscoveryPipeline`，`__init__(self, use_qwen: bool = False)` 实例化 `OrchestratorAgent` / `HypothesisAgent` / `ExperimentAgent` / `ReflectionAgent`
  - [x] SubTask 3.2：实现 `run_full_cycle(self, env_input: dict, max_iterations: int = 3) -> ResearchState`：调 `orchestrator.run(env_input)` → 进入 `for iteration in range(1, max_iterations+1)` 循环，每次执行 `hypothesis.generate(state)` → `experiment.run_validation(state)` → `reflection.reflect(state)` → 记录到 `state.metadata["iterations"]`；`confidence_score >= 0.7` 或达到 `max_iterations` 时退出
  - [x] SubTask 3.3：在循环末尾实现"假设修正"逻辑：若 `confidence_score < 0.7` 且未到 `max_iterations`，把 `state.reflection["issues"]` 注入到 `state.metadata["hypothesis_revisions"]` 列表，下一轮 `hypothesis.generate` 时读取该列表作为修正提示
  - [x] SubTask 3.4：实现 `export_report(self, state: ResearchState, filepath: Optional[str] = None) -> str` 调用 `ReportGenerator(state).save_to_file(filepath)`；默认路径 `config.REPORTS_DIR / f"report_{state.metadata['created_at'].replace(':','-')}.md"`
  - [x] SubTask 3.5：执行（`max_iterations=1`，30×30 地图）：
    ```bash
    python -c "from agents.pipeline import ScientificDiscoveryPipeline; \
    sp=ScientificDiscoveryPipeline(); \
    result=sp.run_full_cycle({...}, max_iterations=1); \
    print(result.metadata.get('iterations',[]))"
    ```
    验证输出至少 1 个迭代 dict（`iterations count: 1`）✓
  - [x] SubTask 3.6：修复循环导入：把 `from reports.report_generator import ReportGenerator` 从模块级挪到 `export_report` 方法体内（延迟导入），打断 `agents → pipeline → reports` 与 `reports → agents` 的环

- [x] Task 4（提示词 5-4）：新建 `reports/__init__.py` 与 `reports/report_generator.py` 实现 `ReportGenerator`
  - [x] SubTask 4.1：创建 `reports/__init__.py`，导出 `ReportGenerator`
  - [x] SubTask 4.2：在 `reports/report_generator.py` 定义 `class ReportGenerator`，`__init__(self, state: ResearchState)` 保存 `state` 到 `self.state`
  - [x] SubTask 4.3：实现 `generate(self) -> str`：按 10 个固定顺序二级标题渲染 Markdown（`## 1. 待研究问题 Problem Statement` ... `## 10. 参考论文 References`）；每个字段从 `self.state` 对应字段提取（hypothesis_text / experiment_plan / expected_results / experiment_results / literature_facts 等）
  - [x] SubTask 4.4：实现"10. 参考论文"过滤：调 `CitationAgent(check_doi_online=False).validate_references(literature_facts)` 拿到 `valid` 列表（离线模式下避免外网请求）；若 `valid` 非空则只列 `valid` 条目，否则在引用末尾追加 `> verification_pending: true` 标注
  - [x] SubTask 4.5：报告末尾追加 `---` 分隔符 + `**生成时间**：<ISO-8601>` + `**系统版本**：<pipeline_version>`
  - [x] SubTask 4.6：实现 `save_to_file(self, filepath: Optional[str] = None) -> str`：默认目录 `config.REPORTS_DIR`（`reports/generated_reports/`），自动 `os.makedirs(..., exist_ok=True)`；拼接 `f"report_{timestamp}.md"`；返回绝对路径
  - [x] SubTask 4.7：执行最小冒烟（30×30 简化版）：
    ```python
    gen = ReportGenerator(rs)
    path = gen.save_to_file()
    assert os.path.exists(path)
    for i in range(1, 11): assert f'## {i}.' in text
    ```
    验证 `reports/generated_reports/` 下存在 `.md` 文件；10 个二级标题齐全 ✓

- [x] Task 5（提示词 5-1 ~ 5-4）：更新 `agents/__init__.py` 导出
  - [x] SubTask 5.1：导出 `ExperimentAgent`（来自 `agents.experiment_agent`）
  - [x] SubTask 5.2：导出 `ScientificDiscoveryPipeline`（来自 `agents.pipeline`）
  - [x] SubTask 5.3：执行
    ```bash
    python -c "from agents import ExperimentAgent, ScientificDiscoveryPipeline, HypothesisAgent, ResearchState; print('imports OK')"
    ```
    验证全部可导入，输出 `imports OK` ✓

# Task Dependencies

- Task 1（HypothesisAgent 4 段结构化）独立，可最先开始；依赖 Phase 4 的 `ResearchState`（已有）✓
- Task 2（ExperimentAgent）依赖 Task 1（需 `state.hypothesis["experiment_plan"]`），独立于 Task 3 / Task 4 ✓
- Task 3（Pipeline 闭环）依赖 Task 1（HypothesisAgent v2）、Task 2（ExperimentAgent）、Task 4（ReportGenerator）；可与 Task 5 并行 ✓
- Task 4（ReportGenerator）独立，仅依赖 `ResearchState` 与 `CitationAgent`；可与 Task 1 / Task 2 并行 ✓
- Task 5（模块导出）依赖 Task 1 ~ Task 4 全部完成 ✓
- 整体收口（验证命令）依赖 Task 1 ~ Task 5 全部完成 ✓
