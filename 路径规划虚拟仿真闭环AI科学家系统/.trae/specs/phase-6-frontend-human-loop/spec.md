# Phase 6：前端展示与人在回路升级 Spec

## Why

Phase 5 完成了后端"假设生成—实验验证"闭环，系统现在能够产出丰富的结构化数据：10 维算法评分、12 个智能体的推理链、完整的 `ResearchState` 以及 SQLite 实验记录。但当前 Streamlit GUI 的 4 个 Tab 展示能力严重不足——Tab 1 仅支持手动滑块调参、无法加载外部地图文件或 Benchmark；Tab 2 只展示 4 维雷达图和简单排名；Tab 3 的推理链仅列出 7 个无详细信息的折叠项；Tab 4 报告展示不完整且缺少人在回路交互。本阶段需要全面升级 4 个 Tab 的前端展示能力，并将 `need_human_check` 信号接入 GUI 提供人在回路交互面板。

## What Changes

- **Tab 1 升级**：新增文件上传区域（CSV/JSON/.map/.scen/.npy → `MapParser` 自动解析）、Benchmark 下拉菜单（调用 `BenchmarkLoader.list_available_maps()`）、4 个随机地图预设模板按钮、优化偏好 radio（耗时优先/成功率优先/路径最短/平衡模式）、算力约束 tooltip 增强
- **Tab 2 升级**：扩展为 10 维指标展示（柱状图 + 雷达图）、新增障碍物聚类数/瓶颈通道数/分布熵指标卡片、Benchmark 实际运行结果对比表格（10 列）、历史数据库偏差提示、评分颜色编码（绿≥0.8 / 黄0.5~0.8 / 红<0.5）
- **Tab 3 升级**：`render_reasoning_chain` 从 7 步扩展为 12 个智能体可展开卡片（Data / Map Analysis / Environment / Literature / Knowledge / Rule / Evaluation / Parameter / Decision / Hypothesis / Reflection / Human-Loop），每个卡片带彩色状态边框，支持一键展开/折叠全部
- **Tab 4 升级**：完整 10 字段 Markdown 报告渲染（分隔线 + Plotly 内嵌图表 + DOI 可点击链接）、3 种导出按钮（Markdown / JSON / CSV）、人在回路面板（红色 alert + 优化优先级调整 + 质疑结论输入 + 重分析触发）
- **涉及文件**：`gui/streamlit_app.py`（重度修改）、`gui/visualization.py`（新增辅助函数）

## Impact

- Affected specs：
  - `phase-4-multi-agent-orchestration`：间接影响（Tab 3 推理链展示依赖 `ResearchState` / `decision` 结构）
  - `phase-5-hypothesis-experiment-loop`：间接影响（Tab 4 报告渲染依赖 `ResearchState` 10 字段和 `hypothesis` 结构）
- Affected code：
  - `gui/streamlit_app.py`（4 个 Tab 全部修改，新增 `execute_decision_pipeline_v2` 支持文件/benchmark/偏好输入）
  - `gui/visualization.py`（新增 `draw_10d_bar` / `draw_10d_radar` / `draw_benchmark_table` / 重写 `render_reasoning_chain` / 新增 `render_human_loop_panel`）
  - `data/benchmark_loader.py`（Tab 1 引用，不修改）
  - `map/map_parser.py`（Tab 1 引用，不修改）

## ADDED Requirements

### Requirement: Tab 1 — 文件上传与 Benchmark 选择

`gui/streamlit_app.py` 的 Tab 1（🗺 地图参数）SHALL 在现有滑块参数区上方新增以下输入组件：

1. **文件上传区域**：使用 `st.file_uploader` 接受 `["csv", "json", "map", "scen", "npy"]` 类型，支持多文件（`accept_multiple_files=False`，单次只处理一个文件）。上传后自动调用 `MapParser().parse(uploaded_file)` 解析为 grid，并写入 `st.session_state`。
2. **Benchmark 选择**：使用 `st.selectbox` 下拉菜单展示 `BenchmarkLoader().list_available_maps()` 返回的 9 个 DAO 地图集名称。选中后调用 `BenchmarkLoader().load_map(map_name)` 加载地图。与文件上传互斥——上传文件后禁用 Benchmark 下拉，反之亦然。
3. **随机地图模板按钮**：4 个 `st.button` 横向排列，标签分别为"低障碍(15%)"、"中障碍(35%)"、"高障碍(65%)"、"迷宫型(50%)"，点击后自动设置对应 `obstacle_ratio` 值并重新生成地图。
4. **优化偏好**：在算力约束 radio 下方新增 `st.radio`，选项 `["耗时优先", "成功率优先", "路径最短", "平衡模式"]`，默认"平衡模式"，作为 `optimization_preference` 传入 `execute_decision_pipeline_v2`。
5. **算力约束 tooltip**：保留原 `compute_limit` radio，在 label 旁添加 `help` 参数说明"low=受限 / medium=标准 / high=充足"。

#### Scenario: 上传 CSV 文件后自动预览
- **WHEN** 用户在 Tab 1 上传一个有效的 CSV 地图文件（如 `test.csv`）
- **THEN** Tab 1 的地图预览区域自动显示解析后的栅格地图，同时参数摘要区更新地图尺寸和障碍物占比

#### Scenario: 选择 Benchmark 地图
- **WHEN** 用户从 Benchmark 下拉菜单选择 `"dao/arena"`
- **THEN** 系统调用 `BenchmarkLoader().load_map("dao/arena")` 加载并解析地图，自动更新地图预览

#### Scenario: 模板按钮快速设置
- **WHEN** 用户点击"迷宫型(50%)"模板按钮
- **THEN** 障碍物占比 slider 自动更新为 0.50，连通性设为 0.40，拓扑随机性设为 0.80，并重新生成地图

### Requirement: Tab 2 — 10 维指标展示与 Benchmark 对比

`gui/streamlit_app.py` 的 Tab 2（📊 环境分析）SHALL 扩展展示内容：

1. **保留原有展示**：地图预览、障碍物占比/连通性/拓扑随机性/综合复杂度指数仪表盘、场景等级
2. **新增地图结构特征卡片**：展示障碍物聚类数、瓶颈通道数、分布熵（来自 `MapAnalyzer.analyze()` 的 `features` 字典）
3. **新增 10 维指标评分柱状图**：调用 `visualization.py` 中新增的 `draw_10d_bar(top_algorithm_detail)` 绘制当前推荐算法的 10 个维度分解柱状图（含 `time_score` / `length_score` / `success_score` / `stability_score` / `smoothness_score` / `safety_score` / `expanded_nodes_score` / `compute_cost_score` / `robustness_score` / `penalty`），颜色按绿/黄/红编码
4. **新增五算法 10 维雷达图**：调用 `visualization.py` 中新增的 `draw_10d_radar(ranking)` 绘制 5 算法 × 10 维雷达图（替代原 4 维雷达图）
5. **新增实验对比结果表格**：使用 `st.dataframe` 展示 `BenchmarkRunner` 实际运行结果的 10 个指标列（`algorithm` / `avg_time` / `avg_path_length` / `success_rate` / `stability_score` / `smoothness` / `safety_score` / `expanded_nodes` / `compute_cost` / `robustness`）
6. **新增历史偏差提示**：对比 `benchmark_results` 与 `knowledge_records` 中同场景等级的均值，若某指标偏差 > 20%，用 `st.warning` 提示
7. **评分颜色编码**：所有评分值用 `st.markdown` 渲染为彩色标签——`≥0.8` 绿色、`0.5~0.8` 黄色、`<0.5` 红色

#### Scenario: Tab 2 展示 10 维柱状图
- **WHEN** 用户执行一次完整分析后在 Tab 2 查看
- **THEN** 柱状图包含 10 个维度的柱形（`time_score` / `length_score` 等），每根柱子颜色按阈值编码

#### Scenario: 五算法 10 维雷达图
- **WHEN** `decision["ranking"]` 包含 5 个算法的评分详情
- **THEN** 雷达图显示 10 个轴（10 个评分维度），5 条不同颜色的折线代表 5 个算法

### Requirement: Tab 3 — 12 智能体推理链卡片

`gui/streamlit_app.py` 的 Tab 3（🤖 智能体推理）和 `gui/visualization.py` 的 `render_reasoning_chain` SHALL 升级：

1. **12 个智能体卡片**（每个用 `st.expander` 折叠）：
   - **Data Agent**：展示输入校验结果（字段完整性、数据类型）、数据来源类型（手动输入/文件上传/Benchmark）
   - **Map Analysis Agent**：地图结构特征详情（聚类数、瓶颈数、熵值、连通区域数）
   - **Environment Agent**：场景分级依据（obstacle_ratio 阈值判断）、复杂度计算公式和各项权重
   - **Literature Agent**：引用的文献事实列表、来源论文标题（来自 `ResearchState.literature_facts` 或 decision metadata）
   - **Knowledge Agent**：检索到的历史实验记录数、覆盖的场景等级分布
   - **Rule Agent**：触发的规则编号和名称、惩罚项详情（惩罚值、触发条件）
   - **Evaluation Agent**：10 维评分详细计算过程（每维归一化前值、归一化后值、权重、加权得分）
   - **Parameter Agent**：推荐的超参数详情（来自 `st.session_state.params`，JSON 格式化展示）
   - **Decision Agent**：最终决策（推荐算法名、综合得分、置信度）、5 算法排名表
   - **Hypothesis Agent**：生成的科学假设文本（4 段结构化：假设正文/实验方案/预期结果/边界条件）
   - **Reflection Agent**：反思结果（假设是否得到支持、confidence_score）、发现的问题列表
   - **Human-Loop Agent**：触发的人工校验项（need_human_check 原因、决策接近度）
2. **彩色边框状态标识**：每个 expander 标题用 `st.markdown` 渲染彩色标签——🟢 绿色=通过、🟡 黄色=警告、🔴 红色=异常
3. **一键展开/折叠**：Tab 3 顶部提供"展开全部"/"折叠全部"按钮，通过 `st.session_state` 控制所有 expander 的 `expanded` 参数

#### Scenario: 推理链展示 12 个卡片
- **WHEN** 用户执行一次完整分析后切换到 Tab 3
- **THEN** 至少展示 8 个可展开的智能体推理卡片（取决于流水线执行了哪些智能体），每个卡片带有彩色状态标识

#### Scenario: 一键展开全部
- **WHEN** 用户点击"展开全部"按钮
- **THEN** 所有智能体卡片同时展开，无需逐个点击

### Requirement: Tab 4 — 完整 10 字段报告与人机交互

`gui/streamlit_app.py` 的 Tab 4（📄 研究报告）SHALL 升级：

1. **完整 10 字段报告渲染**：
   - 使用 `st.markdown` 渲染 Markdown 格式报告，每个字段间用 `st.divider()` 分隔
   - `实验结果` 字段内嵌 Plotly 柱状图和雷达图（调用 `visualization.py` 函数）
   - `参考论文` 字段中识别 DOI 和 URL，渲染为可点击链接
2. **3 种导出按钮**（横向排列在报告底部）：
   - "📥 导出 Markdown 报告"：调用 `generate_markdown_report` 生成 `.md` 并供下载
   - "📥 导出 JSON 数据"：将完整 `st.session_state.decision` + `st.session_state.hypothesis` + `st.session_state.env_input` + `st.session_state.benchmark_results` 序列化为 JSON 供下载
   - "📥 导出实验数据 CSV"：从 `ExperimentDB` 查询当前场景的实验记录，导出为 CSV 供下载
3. **人在回路面板**：
   - 当 `decision` 中 `need_human_check == True` 或排名前 2 名得分差 < 0.05 时，Tab 4 顶部显示红色 `st.error` alert："⚠️ AI 决策存在不确定性，请人工审核"
   - 提供"调整优化优先级"下拉菜单（选项同 Tab 1 的优化偏好）
   - 提供"质疑结论"文本输入框，允许用户输入反馈
   - "提交反馈并重新分析"按钮：将用户反馈合并到 `env_input["human_feedback"]` 并重新执行决策流水线

#### Scenario: 完整报告渲染
- **WHEN** 用户执行分析后切换到 Tab 4
- **THEN** 看到完整的 10 字段报告（而非之前仅 10 个 expander），每个字段用分隔线隔开，实验结果字段内嵌 Plotly 图表

#### Scenario: JSON 导出
- **WHEN** 用户点击"📥 导出 JSON 数据"
- **THEN** 浏览器下载一个 `.json` 文件，包含完整决策数据、假设数据和环境输入

#### Scenario: 人在回路触发
- **WHEN** `need_human_check == True`
- **THEN** Tab 4 顶部显示红色 alert，下方出现人在回路交互面板

## MODIFIED Requirements

### Requirement: execute_decision_pipeline 支持额外输入（来自 Phase 0 / Phase 4）

`gui/streamlit_app.py` 中新增 `execute_decision_pipeline_v2(map_width, map_height, obstacle_ratio, connectivity, topology_randomness, compute_limit, random_seed, start_x, start_y, target_x, target_y, dynamic_change_rate, optimization_preference, grid_from_file)` 函数。该函数在原有 `execute_decision_pipeline` 基础上：
- 接收 `optimization_preference` 参数（字符串，传入 `env_input`）
- 接收 `grid_from_file` 参数（可选 `np.ndarray`，优先于随机生成的地图）
- 保持与旧版相同的 `st.session_state` 写入逻辑

### Requirement: render_reasoning_chain 函数签名重写（来自 Phase 4）

`gui/visualization.py` 中 `render_reasoning_chain(decision)` 函数签名不变，但内部实现从 7 步静态列表升级为 12 个智能体动态卡片。旧调用方 `streamlit_app.py` 中 `render_reasoning_chain(decision)` 调用行不变。

## REMOVED Requirements

无。所有旧版 UI 组件（滑块、地图预览、排名柱状图等）均保留，仅在基础上扩展。
