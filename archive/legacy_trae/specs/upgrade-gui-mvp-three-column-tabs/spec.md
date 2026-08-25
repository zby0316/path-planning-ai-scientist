# 基础版 MVP GUI 三栏 + Tab 升级 Spec

## Why
当前 `ai_scientist_path_planning/gui/streamlit_app.py` 是一个约 142 行的单页 Streamlit 应用（仅 sidebar + 双栏布局），并且 `visualization.py` 仅有 3 个图表函数（`draw_grid` / `draw_ranking_bar` / `draw_radar`），无法支撑"地图参数 → 环境分析 → 智能体推理 → 研究报告"完整工作流的可视化呈现。本变更以 `07-基础版MVP GUI搭建执行方案.md` 为依据，把 GUI 升级为"顶部 4 Tab + 三栏 / 双栏 / 全宽"专业布局，让"输入 → 分析 → 推理 → 报告"全流程在同一页面内可被依次查看、对比、下载。

## What Changes
- **重写** `gui/streamlit_app.py`：升级为顶部 4 Tab + 顶部 page_config + 完整 Session State 管理的多面板页面（约 350 行）。
  - 顶部 Tab：`🗺 地图参数` / `📊 环境分析` / `🤖 智能体推理` / `📄 研究报告`
  - Tab1（左:中:右 = 1:2:1）：输入面板 / 地图预览 / 参数摘要
  - Tab2（1:1 + 1:1）：场景分析卡片 / 排名柱状图 / 雷达图 / Benchmark 数据表
  - Tab3（1:1）：决策结果卡片 / 指标评分详情 / Qwen 解释 / 推理链 / 推荐参数
  - Tab4（全宽）：10 段科学假设 expander + Markdown / PDF / 重新生成 三个按钮
  - 抽取 `execute_decision_pipeline(...)` 与 `regenerate_hypothesis()` 独立函数
  - 抽取 `render_decision_card(decision)`、`render_reasoning_chain(decision)`、`generate_markdown_report(...)` 辅助函数
- **扩展** `gui/visualization.py`：在原 3 个函数基础上新增 6 个辅助函数（约 200 行），其中 `draw_metric_cards` 与 `draw_scene_indicator` 引入 `plotly`（详见 Impact 段）。
- **新增** `map/map_analyzer.py`（如不存在）：`MapAnalyzer` 类，封装 `analyze(grid, start, target) -> dict` 特征输出（`scene_level` / `complexity_index` 等），供 Tab1 中异常降级外的常规调用。
- **新增** `agents/parameter_agent.py`（如不存在）：`ParameterAgent` 类，提供 `recommend(env_input, decision) -> dict` 输出推荐参数 JSON，供 Tab3 "推荐算法参数"面板展示。
- **更新** `requirements.txt`：补充 `plotly>=5.15.0`（按执行方案 §2.1 要求）。
- **不修改** `agents/explanation_agent.py`、`agents/hypothesis_agent.py`、`map/map_generator.py`、`map/connectivity_checker.py`、`evaluation/benchmark.py`、`main.py` 等后端模块；只在前端做调用。

## Impact
- Affected specs: GUI（前端展示与交互）、报告输出（Markdown 下载）。
- Affected code:
  - `ai_scientist_path_planning/gui/streamlit_app.py`（重写）
  - `ai_scientist_path_planning/gui/visualization.py`（扩展）
  - `ai_scientist_path_planning/requirements.txt`（追加 1 行）
  - `ai_scientist_path_planning/map/map_analyzer.py`（可能新建）
  - `ai_scientist_path_planning/agents/parameter_agent.py`（可能新建）
- 受影响上下游：
  - `streamlit_app.py` 强依赖 `MapGenerator.generate`、`ConnectivityChecker.is_reachable`、`BenchmarkRunner.run` / `print_table`、`PathPlanningDecisionSystem.decide`、`ExplanationAgent.explain`、`HypothesisAgent.generate`、`MapAnalyzer.analyze`（如可用）、`ParameterAgent.recommend`（如可用）。
  - `streamlit_app.py` 通过 `st.session_state` 在 4 个 Tab 间共享 `grid` / `start` / `target` / `env_input` / `decision` / `benchmark_results` / `features` / `params` / `hypothesis`。
  - `visualization.py` 中 `draw_metric_cards` / `draw_scene_indicator` 使用 Plotly（属 §2.1 新增依赖）；其他函数保持 Matplotlib，无新依赖。

## ADDED Requirements

### Requirement: 顶部 4 Tab 全局导航
`streamlit_app.py` 顶部必须通过 `st.tabs([...])` 提供 4 个 Tab：`🗺 地图参数`、`📊 环境分析`、`🤖 智能体推理`、`📄 研究报告`。每个 Tab 的入口处使用对应的 `with tab_xxx:` 块包裹该页所有内容。

#### Scenario: 启动并切换 Tab
- **WHEN** 用户运行 `streamlit run gui/streamlit_app.py` 并打开页面
- **THEN** 页面顶部显示 4 个 Tab 标签；用户点击任一 Tab 可切换到对应视图，且 Session State 中的数据在 Tab 之间保持一致。

### Requirement: Session State 初始化
`main()` 函数开头必须为下列键创建初始值（缺则写入）：`decision`、`benchmark_results`、`grid`、`start`、`target`、`env_input`、`features`、`params`、`hypothesis`。

#### Scenario: 首次进入页面
- **WHEN** 用户首次打开页面
- **THEN** 上述 Session State 键均已存在且为初始值（`None` / `{}`），不会触发 `KeyError`。

### Requirement: Tab1 地图参数三栏布局
Tab1 必须使用 `st.columns([1, 2, 1])` 三栏布局：
- 左栏：地图参数输入面板（含算力 radio、连通性/拓扑随机性滑块、起点终点、动态变化率、随机种子、"开始多智能体分析"、"重新生成地图"两个按钮）。
- 中栏：地图预览（调用 `draw_grid(...)` 渲染并 `st.pyplot` 显示）。
- 右栏：参数摘要（`st.metric` 列表展示）。

#### Scenario: 调整参数并点击"开始多智能体分析"
- **WHEN** 用户在左栏调整滑块/数字输入并点击 `▶ 开始多智能体分析`
- **THEN** `execute_decision_pipeline(...)` 被调用，依次执行：生成地图 → 连通性检查（不连通最多重试 5 次）→ Benchmark 运行 → 决策系统 → 地图分析（如可用）→ Qwen 解释与科学假设生成；流程结束后 `st.success("✅ 分析完成！")` 显示并 `st.rerun()`。

### Requirement: 执行决策管线函数 `execute_decision_pipeline`
将原 `streamlit_app.py` 中的核心决策流程抽取为独立函数 `execute_decision_pipeline(map_width, map_height, obstacle_ratio, connectivity, topology_randomness, compute_limit, random_seed, start_x, start_y, target_x, target_y, dynamic_change_rate)`，函数内部把中间结果写入 `st.session_state`。`MapAnalyzer` 缺失时使用 `try/except ImportError` 降级为 `{"scene_level": decision.get("scene_level", "unknown")}`。

#### Scenario: MapAnalyzer 缺失场景
- **WHEN** 环境中未安装 `map/map_analyzer.py`
- **THEN** 函数不抛异常，`st.session_state.features` 退化为包含 `scene_level` 的最小字典。

### Requirement: Tab2 环境分析双栏布局
Tab2 必须先校验 `st.session_state.decision` 是否为 `None`，为空时显示 `st.info("请先在「地图参数」标签页中执行分析。")`；否则：
- 上方左右两栏：场景等级 + 复杂度指数 + 推荐算法 / 综合得分 卡片；右侧为算法综合评分排名柱状图（`draw_ranking_bar`）。
- 下方左右两栏：多指标雷达图（`draw_radar`）；右侧为 `BenchmarkRunner.print_table` 输出。

#### Scenario: 决策完成后切换到 Tab2
- **WHEN** 用户在 Tab1 完成分析后切到 Tab2
- **THEN** 页面渲染场景等级、复杂度指数、推荐算法、综合得分、排名柱状图、雷达图、Benchmark 表格 6 项内容。

### Requirement: Tab3 智能体推理布局
Tab3 校验 `decision is not None` 后，左右两栏分别展示：
- 左栏：决策结果卡片（`render_decision_card`）→ 指标评分详情（5 个 `st.metric`：耗时/路径/成功率/稳定性/规则惩罚）→ Qwen 解释（`ExplanationAgent.explain` 输出 `st.info`）。
- 右栏：7 步推理链 `render_reasoning_chain`（① 数据接收 → ⑦ 参数推荐，每步 `st.expander` 包裹 `st.success`）→ 推荐算法参数（`st.session_state.params` 以 `st.code` JSON 形式展示）。

#### Scenario: 查看推荐算法参数
- **WHEN** `st.session_state.params` 已存在
- **THEN** Tab3 右栏底部以 JSON 格式代码块展示该参数对象。

### Requirement: Tab4 研究报告布局
Tab4 校验 `hypothesis is not None` 后，逐项以 `st.expander` 渲染 10 个标准字段（待研究问题 / 解决思路 / 必要技术手段 / 数据集 / 论文标题 / 摘要 / 方法论 / 实验设计 / 实验结果 / 参考论文），内容为空时显示 `*待生成*`；底部三列按钮：`📥 下载 Markdown`（通过 `st.download_button` 下载 `generate_markdown_report(hypothesis, decision, env_input)` 的输出，文件名 `ai_scientist_research_report.md`）/ `📥 下载 PDF`（disabled，help 说明优化版实现）/ `🔄 重新生成`（`on_click=regenerate_hypothesis`）。

#### Scenario: 下载 Markdown 报告
- **WHEN** 用户点击 `📥 下载 Markdown`
- **THEN** 浏览器下载名为 `ai_scientist_research_report.md` 的文件，内容为按 10 段结构组织的 Markdown 文本。

#### Scenario: 点击"重新生成"
- **WHEN** 用户点击 `🔄 重新生成`
- **THEN** 重新调用 `ExplanationAgent.explain` + `HypothesisAgent.generate`，更新 `st.session_state.hypothesis` 并触发页面刷新。

### Requirement: visualization.py 新增辅助函数
`gui/visualization.py` 在原 3 个函数基础上新增（仅作为可选辅助，由 streamlit_app.py 按需调用）：
- `draw_metric_cards(metrics: dict)`：用 Plotly 渲染指标卡片组合图。
- `draw_scene_indicator(scene_level: str, complexity: float)`：用 Plotly 仪表盘（gauge+number）展示场景等级。

#### Scenario: 引入 Plotly
- **WHEN** streamlit_app.py 调用 `draw_metric_cards` 或 `draw_scene_indicator`
- **THEN** 函数正确返回 `plotly.graph_objects.Figure`，调用方可用 `st.plotly_chart(fig)` 渲染。
- **NOTE** 原 `draw_grid` / `draw_ranking_bar` / `draw_radar` 三个 Matplotlib 函数保持不变，向后兼容。

### Requirement: MapAnalyzer 适配
如 `map/map_analyzer.py` 存在，`MapAnalyzer().analyze(grid, start, target)` 必须返回至少包含 `scene_level`、`complexity_index` 两个键的字典；如不存在则按 `execute_decision_pipeline` 中的 `try/except` 降级路径处理。

#### Scenario: Tab1 调 analyze
- **WHEN** 决策管线调用 `analyzer.analyze(...)`
- **THEN** 若模块存在则写入 `st.session_state.features`；否则 `features` 仅含 `scene_level`，不抛错。

### Requirement: ParameterAgent 适配
如 `agents/parameter_agent.py` 存在，`ParameterAgent().recommend(env_input, decision)` 必须返回可被 `json.dumps` 序列化的参数字典；其结果在 Tab3 中以 `st.code` 展示。模块缺失时 `st.session_state.params` 维持初始值 `None`，Tab3 跳过 JSON 展示。

#### Scenario: 缺失 ParameterAgent
- **WHEN** `agents/parameter_agent.py` 不存在
- **THEN** Tab3 右栏底部不显示 `st.code` 块，但不抛异常。

## MODIFIED Requirements
（无：本次变更不对现有后端模块逻辑做修改，仅新增与升级 GUI；既有需求保持不变。）

## REMOVED Requirements
（无：不删除任何文件、不删除任何函数。）
