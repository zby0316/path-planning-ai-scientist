# Phase 5：假设生成—实验验证闭环 Spec

## Why

Phase 4 已经把多智能体协同的"骨架"搭好：12+ 智能体在 `OrchestratorAgent` 调度下围绕 `ResearchState` 流水线化运行，并产出 `decision` / `explanation` / `hypothesis`（仅含 `best_algorithm` / `scene_level` / `text` 三字段）/ `reflection` 等结果。但当前 `HypothesisAgent` 输出的是一段纯文本"研究计划"，既没有可执行的实验方案，也没有预期指标与边界条件，难以直接驱动真正的实验验证；同时系统缺少一个"假设 → 跑实验 → 反思 → 修正"的闭环，决策结果是否站得住脚完全靠人工判断。本阶段需要：升级 `HypothesisAgent` 让假设变成"4 段结构化"且绑定实验方案；新增 `ExperimentAgent` 自动在 50 张随机地图上跑 5 算法 × 5 重复并写入 `ExperimentDB`；新增 `ScientificDiscoveryPipeline` 把 Hypothesis → Experiment → Reflection 串成可重复运行的闭环（最多 3 次迭代修正）；新增 `ReportGenerator` 严格按 10 字段模板把 `ResearchState` 渲染为 Markdown 报告并落盘到 `reports/generated_reports/`。

## What Changes

- 升级 `agents/hypothesis_agent.py`：重写 `HYPOTHESIS_SYSTEM_PROMPT`、新增 `HYPOTHESIS_USER_TEMPLATE` 强调"4 段结构化"输出；`HypothesisAgent.generate(state)` 改为接收 `ResearchState` 并返回 `ResearchState`（同时保留旧 `generate(env, decision, explanation)` 签名）；`HypothesisAgent._default_hypothesis` 升级为 10 字段模板（待研究问题、科学假设、解决思路、必要技术手段、数据集、论文标题、摘要、方法论、实验设计、参考论文）；`hypothesis` 对象升级为 `{"hypothesis_text": str, "experiment_plan": dict, "expected_results": dict, "boundary_conditions": list}`（提示词 5-1）。
- 在 `llm/prompt_templates.py` 末尾追加 `HYPOTHESIS_SYSTEM_PROMPT` 的"4 段结构化"版本与对应 `HYPOTHESIS_USER_TEMPLATE`（提示词 5-1）。
- 新建 `agents/experiment_agent.py` 中的 `ExperimentAgent` 类，依赖既有 `ExperimentDB`（`data/experiment_db.py`）与 `BenchmarkRunner`（`evaluation/benchmark.py`），提供 `run_validation(state)` 与 `compare_with_hypothesis(state)`，把每张地图的 5 算法 × 5 重复结果写入 `ExperimentDB`，汇总成功率/耗时/路径长度等指标写入 `state.experiment_results`，并设置 `state.metadata["hypothesis_supported"]`（提示词 5-2）。
- 新建 `agents/pipeline.py` 中的 `ScientificDiscoveryPipeline` 类，串联 `OrchestratorAgent → HypothesisAgent → ExperimentAgent → ReflectionAgent`，并在 `confidence_score < 0.7` 且未达到 `max_iterations` 时修正假设重跑；提供 `export_report(state, filepath)` 把最终结果导出为 Markdown 报告（提示词 5-3）。
- 新建 `reports/__init__.py` 与 `reports/report_generator.py` 中的 `ReportGenerator` 类，提供 `generate(state)` / `save_to_file(filepath)`，按 10 字段模板渲染 Markdown（提示词 5-4）。
- 更新 `agents/__init__.py` 导出 `ExperimentAgent` 与 `ScientificDiscoveryPipeline`。
- 保留 Phase 0/1/4 既有契约：`HypothesisAgent.generate(env, decision, explanation)` 旧签名保留；`HypothesisAgent.generate_state(state)` 旧入口保留；`main.py` / `tests/` 既有用例不受影响。

## Impact

- Affected specs：
  - `phase-0-compliance-and-baseline`：间接影响（既有 `main.py` / `tests/` 不破坏）。
  - `phase-1-data-input-upgrade`：间接影响（既有 `MapParser` 行为不变）。
  - `phase-4-multi-agent-orchestration`：直接影响（`HypothesisAgent` 内部结构升级，hypothesis 字段从 3 字段扩为 4 字段并嵌套 `experiment_plan` / `expected_results` / `boundary_conditions`）。
- Affected code：
  - `agents/hypothesis_agent.py`（重写：4 段结构化 + `generate(state)` 入口 + 10 字段默认模板）
  - `llm/prompt_templates.py`（追加 `HYPOTHESIS_SYSTEM_PROMPT` v2 / `HYPOTHESIS_USER_TEMPLATE` v2）
  - `agents/experiment_agent.py`（新建：`ExperimentAgent`）
  - `agents/pipeline.py`（新建：`ScientificDiscoveryPipeline`）
  - `agents/__init__.py`（导出 `ExperimentAgent` / `ScientificDiscoveryPipeline`）
  - `reports/__init__.py`（新建）
  - `reports/report_generator.py`（新建：`ReportGenerator`）
  - `config.py`（无需修改：`REPORTS_DIR = "reports/generated_reports"` 已存在）

## ADDED Requirements

### Requirement: HypothesisAgent 4 段结构化假设

`agents/hypothesis_agent.py` 的 `HypothesisAgent` SHALL 升级，要求：

1. `llm/prompt_templates.py` SHALL 提供 `HYPOTHESIS_SYSTEM_PROMPT` v2 与 `HYPOTHESIS_USER_TEMPLATE` v2。`HYPOTHESIS_SYSTEM_PROMPT` SHALL 至少声明：
   - 角色：路径规划 AI Scientist；
   - 严格要求：仅输出合法 JSON，不要输出 Markdown 代码块、解释或多余文本；
   - JSON 顶层字段必须为对象，且包含 `hypothesis_text` / `experiment_plan` / `expected_results` / `boundary_conditions` 4 个键；
   - `hypothesis_text` SHALL 采用「在 X 条件下，算法 Y 相比 Z 在指标 W 上有显著优势」的句式；
   - `experiment_plan` SHALL 至少包含 `maps`（地图数量与规模）、`algorithms`（待比较算法列表）、`runs_per_algorithm`（每算法重复次数）、`metrics`（评估指标列表）4 个字段；
   - `expected_results` SHALL 至少包含 `best_algorithm` / `success_rate_threshold` / `time_budget_seconds` 3 个字段；
   - `boundary_conditions` SHALL 为数组，每项为一句中文边界条件描述（如"地图尺寸 ≥ 100×100"）。
2. `HypothesisAgent.__init__(self, use_qwen: bool = True)` SHALL 保留 `use_qwen` 行为：仅当 `use_qwen=True` 时实例化 `QwenClient`（沿用 Phase 4 离线降级逻辑）。
3. `HypothesisAgent.generate(self, state: ResearchState) -> ResearchState` SHALL 接收 `ResearchState`，调用 LLM 后解析 JSON 输出（解析失败 SHALL 回退到 `_default_hypothesis` 离线规则），最终把 4 段结构化假设写入 `state.hypothesis`。
4. 旧 `HypothesisAgent.generate(self, env, decision, explanation) -> str` 签名 SHALL 保留以兼容 Phase 0/1 调用方；其内部 SHALL 委托到 `generate_state` 或 `_default_hypothesis`。
5. `_default_hypothesis(state)` SHALL 返回包含 10 字段的字符串模板：待研究问题 / 科学假设 / 解决思路 / 必要技术手段 / 数据集 / 论文标题 / 摘要 / 方法论 / 实验设计 / 参考论文；这 10 字段的内容 SHALL 按 `state.env_input` / `state.decision` / `state.literature_facts` / `state.algorithm_records` 填充。
6. `hypothesis` 对象 SHALL 满足结构：
   ```python
   {
     "hypothesis_text": str,
     "experiment_plan": {
       "maps": {"count": int, "width": int, "height": int},
       "algorithms": list[str],
       "runs_per_algorithm": int,
       "metrics": list[str],
     },
     "expected_results": {
       "best_algorithm": str,
       "success_rate_threshold": float,
       "time_budget_seconds": float,
     },
     "boundary_conditions": list[str],
     "raw_text": str,        # 10 字段文本（来自 _default_hypothesis）
     "generated_by": str,    # "qwen" 或 "rule"
   }
   ```

#### Scenario: 离线模式生成假设
- **WHEN** 执行
  ```bash
  python -c "from agents.hypothesis_agent import HypothesisAgent; \
  ha=HypothesisAgent(use_qwen=False); \
  from agents.research_state import ResearchState; \
  rs=ResearchState(env_input={'obstacle_ratio':0.65,'connectivity':0.3}); \
  rs.decision={'best_algorithm':'混合优化算法','scene_level':'高复杂度','ranking':[],'best_score':0.85}; \
  h=ha.generate(rs); print('hypothesis_text' in rs.hypothesis)"
  ```
- **THEN** SHALL 输出 `True`，且 `rs.hypothesis["hypothesis_text"]` 非空

#### Scenario: 4 段结构完整
- **WHEN** 调用 `HypothesisAgent(use_qwen=False).generate(state)` 后检查 `state.hypothesis`
- **THEN** SHALL 同时包含 4 个键 `hypothesis_text` / `experiment_plan` / `expected_results` / `boundary_conditions`

#### Scenario: 旧调用方不受影响
- **WHEN** 调用旧 `HypothesisAgent(use_qwen=False).generate(env_dict, decision_dict, explanation_str)`
- **THEN** SHALL 仍返回字符串（不抛 `TypeError`），与 Phase 0/1 既有行为一致

### Requirement: ExperimentAgent 自动实验验证

`agents/experiment_agent.py` SHALL 提供 `ExperimentAgent` 类，要求：

1. `__init__(self, db: ExperimentDB, benchmark_runner: BenchmarkRunner)` SHALL 接收 `ExperimentDB`（`data/experiment_db.py`）与 `BenchmarkRunner`（`evaluation/benchmark.py`）实例。
2. `run_validation(self, state: ResearchState) -> ResearchState` SHALL：
   - 读取 `state.hypothesis["experiment_plan"]`，若缺失 SHALL 退回到 `_default_experiment_plan(state)`（50 张地图、5 算法、5 重复）；
   - 使用 `MapGenerator` 生成对应规模与障碍率的随机地图（默认 50 张，100×100，与 `state.decision["scene_level"]` 匹配的复杂度）；
   - 对每张地图用 `BenchmarkRunner.run(grid, start, target, n_runs=5)` 跑 5 算法 × 5 重复；
   - 把每条 `algorithm_runs` 通过 `ExperimentDB.insert_run` 写入 `data/experiments/experiments.sqlite`；
   - 按算法聚合 `success_rate`（`success=1` 的比例）、`avg_runtime`（`runtime` 均值）、`avg_path_length`（`path_length` 均值）、`stability_score`（`stability_score` 均值）等，写入 `state.experiment_results`（list of dict，每条对应一个算法的聚合结果）；
   - 调用 `compare_with_hypothesis(state)` 判定假设是否得到支持，并把布尔值写入 `state.metadata["hypothesis_supported"]`；
   - 中途任意步骤抛异常 SHALL 把异常追加到 `state.metadata["errors"]` 并继续（不中断流水线）。
3. `compare_with_hypothesis(self, state) -> bool` SHALL：
   - 读取 `state.hypothesis["expected_results"]["best_algorithm"]`（若缺失则用 `state.decision["best_algorithm"]`）；
   - 读取 `state.experiment_results` 中各算法聚合 `success_rate`；
   - 判定规则：推荐算法 `success_rate > 次优算法 10%` 且 `len(state.experiment_results) ≥ 2`；不满足则返回 `False`；
   - 返回值同时写入 `state.metadata["hypothesis_supported"]` 与 `state.metadata["hypothesis_support_score"]`（0~1 的连续值）。
4. `state.experiment_results` 列表每项 SHALL 至少包含键：`algorithm` / `n_maps` / `success_rate` / `avg_runtime` / `avg_path_length` / `stability_score`。

#### Scenario: 跑通 50 张地图
- **WHEN** 执行
  ```python
  from agents.experiment_agent import ExperimentAgent
  from data.experiment_db import ExperimentDB
  from evaluation.benchmark import BenchmarkRunner
  from agents.research_state import ResearchState
  ea = ExperimentAgent(db=ExperimentDB(), benchmark_runner=BenchmarkRunner())
  rs = ResearchState(env_input={"obstacle_ratio": 0.35, "map_width": 50, "map_height": 50})
  rs.decision = {"best_algorithm": "A*", "scene_level": "中复杂度", "ranking": [], "best_score": 0.8}
  rs = ea.run_validation(rs)
  ```
- **THEN** `len(rs.experiment_results) >= 2`（至少 2 个算法有结果），且 `rs.metadata["hypothesis_supported"] in (True, False)`

#### Scenario: 假设不支持
- **WHEN** `state.hypothesis["expected_results"]["best_algorithm"]` 为 `"A*"`，但 `state.experiment_results` 中 `"ACO"` 的 `success_rate` 比 `"A*"` 高
- **THEN** `state.metadata["hypothesis_supported"] == False`

#### Scenario: 缺省实验方案
- **WHEN** `state.hypothesis` 不含 `experiment_plan`
- **THEN** `run_validation` SHALL 使用 `_default_experiment_plan(state)` 的默认 50 张地图/5 算法/5 重复参数继续运行

### Requirement: ScientificDiscoveryPipeline 假设-验证-反思闭环

`agents/pipeline.py` SHALL 提供 `ScientificDiscoveryPipeline` 类，要求：

1. `__init__(self, use_qwen: bool = False)` SHALL 实例化：`OrchestratorAgent` / `HypothesisAgent` / `ExperimentAgent` / `ReflectionAgent`。
2. `run_full_cycle(self, env_input: dict, max_iterations: int = 3) -> ResearchState` SHALL：
   - 调用 `self.orchestrator.run(env_input)` 获得初始 `ResearchState`；
   - 进入迭代循环（`iteration` 从 1 开始，≤ `max_iterations`）：
     a. 调 `self.hypothesis_agent.generate(state)`（首次基于决策生成假设，后续迭代基于 `state.metadata["iterations"][-1]["issues"]` 修正假设）；
     b. 调 `self.experiment_agent.run_validation(state)`；
     c. 调 `self.reflection_agent.reflect(state)`；
     d. 把本轮 `state.hypothesis` / `state.experiment_results` / `state.reflection` 追加到 `state.metadata["iterations"]` 列表；
     e. 若 `state.reflection.get("confidence_score", 0) >= 0.7` 或 `iteration >= max_iterations` 则退出循环；否则在 `state.decision` 中追加"修正方向"，再次进入循环。
3. `export_report(self, state: ResearchState, filepath: Optional[str] = None) -> str` SHALL 调用 `ReportGenerator(state).save_to_file(filepath)`，默认路径为 `config.REPORTS_DIR / "report_<timestamp>.md"`。
4. 失败时 SHALL 把异常追加到 `state.metadata["errors"]`，并尽量继续后续步骤（不中断整个流水线）。
5. `state.metadata["iterations"]` SHALL 至少包含 `iteration` / `hypothesis_summary` / `hypothesis_supported` / `confidence_score` / `issues` 5 个键。

#### Scenario: 跑通 1 次迭代
- **WHEN** 执行
  ```bash
  python -c "from agents.pipeline import ScientificDiscoveryPipeline; \
  sp=ScientificDiscoveryPipeline(); \
  result=sp.run_full_cycle({'obstacle_ratio':0.65,'map_width':100,'map_height':100,'connectivity':0.3,'topology_randomness':0.7,'compute_limit':'high'}, max_iterations=1); \
  print(result.metadata.get('iterations',[]))"
  ```
- **THEN** SHALL 输出至少 1 个迭代 dict 的列表

#### Scenario: 达到 max_iterations 退出
- **WHEN** `max_iterations=2` 且第 1 次 `confidence_score < 0.7`
- **THEN** `len(state.metadata["iterations"]) == 2`

#### Scenario: 报告导出
- **WHEN** 调用 `sp.export_report(state, filepath="reports/generated_reports/test.md")`
- **THEN** SHALL 在 `filepath` 生成 Markdown 文件，且文件包含 10 个二级标题（提示词 5-4 要求）

### Requirement: ReportGenerator 标准化 10 字段报告

`reports/report_generator.py` SHALL 提供 `ReportGenerator` 类，要求：

1. `__init__(self, state: ResearchState)` SHALL 保存 `state` 到实例属性。
2. `generate(self) -> str` SHALL 渲染包含以下 10 个二级标题的 Markdown 文本（顺序固定）：
   - `## 1. 待研究问题 Problem Statement`
   - `## 2. 解决思路 Rationale`
   - `## 3. 必要技术手段 Technical Details`
   - `## 4. 数据集 Datasets`
   - `## 5. 论文标题 Paper Title`
   - `## 6. 摘要 Paper Abstract`
   - `## 7. 方法论 Methods`
   - `## 8. 实验设计 Experiments`
   - `## 9. 实验结果 Results`
   - `## 10. 参考论文 References`
3. 每个字段 SHALL 自动从 `ResearchState` 对应字段提取内容：
   - 1 / 2 / 3 / 5 / 6 / 7：来自 `state.hypothesis.get("hypothesis_text", "")` 与 `state.hypothesis.get("raw_text", "")`；
   - 4 数据集：来自 `state.env_input` 与 `state.map_features`；
   - 8 实验设计：来自 `state.hypothesis.get("experiment_plan", {})` 与 `state.recommended_params`；
   - 9 实验结果：来自 `state.experiment_results` 与 `state.metadata.get("hypothesis_supported")`；
   - 10 参考论文：来自 `state.literature_facts`，并经过 `CitationAgent().validate_references()` 过滤为 `valid` 集合（network 不可用时降级为"全部纳入"，但要标注 `verification_pending`）。
4. 报告末尾 SHALL 追加：生成时间戳（ISO-8601）与系统版本（`state.metadata["pipeline_version"]`）。
5. `save_to_file(self, filepath: Optional[str] = None) -> str` SHALL：
   - 默认目录为 `config.REPORTS_DIR`（即 `reports/generated_reports/`）；
   - 若 `filepath` 为目录则拼接 `report_<timestamp>.md`，若为完整路径则直接写入；
   - 自动创建父目录（`os.makedirs(..., exist_ok=True)`）；
   - 返回最终写入的文件绝对路径。

#### Scenario: 报告生成与落盘
- **WHEN** 构造一个最小 `ResearchState` 并执行
  ```python
  from reports.report_generator import ReportGenerator
  gen = ReportGenerator(state)
  path = gen.save_to_file()
  ```
- **THEN** SHALL 在 `reports/generated_reports/` 下生成一个 `.md` 文件；该文件 SHALL 包含上述 10 个二级标题

#### Scenario: 10 标题顺序
- **WHEN** 把 `gen.generate()` 输出按行 split 并取以 `## ` 开头的行
- **THEN** SHALL 顺序为 `1.` `2.` `3.` `4.` `5.` `6.` `7.` `8.` `9.` `10.`

#### Scenario: References 过滤
- **WHEN** `state.literature_facts` 同时含 `verified==True` 与 `verified==False` 条目
- **THEN** 报告"10. 参考论文"应只列出 `verified==True` 的条目；若 `CitationAgent` 网络不可用 SHALL 全部纳入并标注 `verification_pending: true`

## MODIFIED Requirements

### Requirement: HypothesisAgent 旧接口保持兼容（来自 Phase 0 / Phase 4）

`HypothesisAgent.generate(self, env: dict, decision: dict, explanation: str) -> str` 与 `HypothesisAgent.generate_state(self, state) -> ResearchState` SHALL 全部保留；本阶段在 `HypothesisAgent` 上**追加** `generate(state: ResearchState) -> ResearchState`（v2 入口，输出 4 段结构化），但**不修改或删除**旧方法签名，以确保 `main.py` 既有调用与 `tests/` 不被破坏。

### Requirement: HYPOTHESIS_SYSTEM_PROMPT 旧版保留（来自 Phase 0）

`llm/prompt_templates.py` SHALL 同时保留 `HYPOTHESIS_SYSTEM_PROMPT`（旧版，Phase 0）与 `HYPOTHESIS_SYSTEM_PROMPT_V2` / `HYPOTHESIS_USER_TEMPLATE_V2`（新版，Phase 5 4 段结构化）；Phase 5 `HypothesisAgent` 引用 V2 版本，旧调用方不受影响。

## REMOVED Requirements

无。
