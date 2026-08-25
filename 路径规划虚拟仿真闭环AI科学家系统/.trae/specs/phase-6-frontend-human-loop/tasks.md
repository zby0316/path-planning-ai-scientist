# Tasks

> 范围：Phase 6 前端展示与人在回路升级，对应提示词 6-1 ~ 6-4。
> 实现阶段需先阅读 `.trae/specs/phase-6-frontend-human-loop/spec.md`。

- [x] Task 1（提示词 6-1）：升级 Tab 1 — 文件上传、Benchmark 选择、模板按钮、优化偏好
  - [x] SubTask 1.1：在 `gui/streamlit_app.py` 的 `tab_map` 区域顶层新增文件上传组件：`st.file_uploader("📁 上传地图文件", type=["csv", "json", "map", "scen", "npy"])`，上传后调用 `MapParser().parse()` 解析，grid 写入 `st.session_state.uploaded_grid`，并更新障碍物占比等参数。需使用 `tempfile` 将 `UploadedFile` 写入临时文件再传给 `MapParser`。
  - [x] SubTask 1.2：新增 Benchmark 下拉菜单：`st.selectbox("📦 选择 Benchmark 地图", options=BenchmarkLoader().list_available_maps())`，选中非空项后调用 `BenchmarkLoader().load_map()` 加载地图并更新 `st.session_state`。与文件上传互斥（任一激活时禁用另一个）。
  - [x] SubTask 1.3：新增 4 个随机地图模板按钮：用 `st.columns(4)` 横向排列，每个按钮点击后通过 `st.session_state` 设置对应的 `obstacle_ratio` / `connectivity` / `topology_randomness` 预设值并触发 `st.rerun()`。预设值：低障碍(15%)→0.15/0.8/0.3、中障碍(35%)→0.35/0.68/0.55、高障碍(65%)→0.65/0.3/0.7、迷宫型(50%)→0.50/0.4/0.8。
  - [x] SubTask 1.4：新增优化偏好 radio：`st.radio("🎯 优化偏好", ["耗时优先", "成功率优先", "路径最短", "平衡模式"], index=3, horizontal=True)`，值存入 `optimization_preference` 变量。
  - [x] SubTask 1.5：增强算力约束 radio 的 `help` tooltip：`help="low=边缘设备（算力受限）/ medium=标准桌面 / high=服务器集群（算力充足）"`。
  - [x] SubTask 1.6：新增 `execute_decision_pipeline_v2` 函数，增加 `optimization_preference` 和 `grid_from_file` 参数，在 `env_input` 中追加 `"optimization_preference"` 字段；若有 `grid_from_file` 则跳过 `MapGenerator.generate()` 直接使用传入 grid。旧 `execute_decision_pipeline` 函数保留不动。
  - [x] SubTask 1.7：修改 Tab 1 地图预览逻辑：优先展示上传/Benchmark 地图（`st.session_state.uploaded_grid`），其次展示随机生成地图。

- [x] Task 2（提示词 6-2）：升级 Tab 2 — 10 维指标展示、Benchmark 对比、颜色编码
  - [x] SubTask 2.1：在 `gui/visualization.py` 中新增 `draw_10d_bar(detail: dict) -> go.Figure` 函数：绘制 10 维评分柱状图。维度键名：`time_score` / `length_score` / `success_score` / `stability_score` / `smoothness_score` / `safety_score` / `expanded_nodes_score` / `compute_cost_score` / `robustness_score` / `penalty`。每根柱子颜色按阈值编码（≥0.8 绿、0.5~0.8 黄、<0.5 红），缺失维度置为 0。
  - [x] SubTask 2.2：在 `gui/visualization.py` 中新增 `draw_10d_radar(ranking: list) -> go.Figure` 函数：绘制 5 算法 × 10 维 Plotly 雷达图（使用 `go.Scatterpolar`），保留原 `draw_radar`（matplotlib 4 维版）不动。
  - [x] SubTask 2.3：在 `gui/streamlit_app.py` 的 Tab 2 中新增地图结构特征卡片区域：从 `st.session_state.features` 提取障碍物聚类数、瓶颈通道数、分布熵，使用 `st.metric` 以 3 列布局展示。
  - [x] SubTask 2.4：在 Tab 2 中新增 10 维指标评分柱状图区域：调用 `draw_10d_bar(top_algorithm_detail)` 并用 `st.plotly_chart` 渲染。
  - [x] SubTask 2.5：在 Tab 2 中新增五算法 10 维雷达图：调用 `draw_10d_radar(decision["ranking"])` 并用 `st.plotly_chart` 渲染。
  - [x] SubTask 2.6：在 Tab 2 中新增 Benchmark 实际运行结果对比表格：从 `st.session_state.benchmark_results` 提取各算法的 10 个指标，构造 `pd.DataFrame`，用 `st.dataframe` 展示。列名：算法/平均耗时/平均路径长度/成功率/稳定性/平滑度/安全得分/扩展节点数/计算开销/鲁棒性。
  - [x] SubTask 2.7：在 Tab 2 中新增历史偏差提示：对比 `benchmark_results` 与 `decision` 中的 `knowledge_records`（若存在），计算同场景等级下成功率和平均耗时的偏差，若偏差 > 20% 则用 `st.warning` 提示。
  - [x] SubTask 2.8：实现评分颜色编码辅助函数 `_score_color(score: float) -> str`：≥0.8 返回 `"green"`，0.5~0.8 返回 `"orange"`，<0.5 返回 `"red"`。在 `draw_10d_bar` 和 Tab 2 的 `st.metric` 中使用。

- [x] Task 3（提示词 6-3）：升级 Tab 3 — 12 智能体推理链卡片
  - [x] SubTask 3.1：重写 `gui/visualization.py` 中的 `render_reasoning_chain(decision, expanded_all=False)` 函数：将原来 7 步静态列表替换为 12 个智能体卡片，每个卡片用 `st.expander` 包裹。卡片数据来源：
    - Data Agent：输入校验结果、数据来源类型
    - Map Analysis Agent：地图结构特征详情（聚类数、瓶颈数、熵值、连通区域数）
    - Environment Agent：场景分级依据、复杂度计算公式
    - Literature Agent：引用的文献事实列表、来源论文
    - Knowledge Agent：检索到的历史实验记录数、覆盖场景
    - Rule Agent：触发的规则、惩罚项详情
    - Evaluation Agent：10 维评分详细计算过程
    - Parameter Agent：推荐的超参数（JSON 格式化展示）
    - Decision Agent：最终决策及排名表
    - Hypothesis Agent：生成的科学假设（4 段结构化）
    - Reflection Agent：反思结果、发现的问题
    - Human-Loop Agent：触发的人工校验项
  - [x] SubTask 3.2：实现彩色状态标识：每个 expander 标题前添加状态 emoji（🟢/🟡/🔴），状态由各智能体的输出决定（有数据且正常=绿，有数据但偏低=黄，无数据或异常=红）。
  - [x] SubTask 3.3：在 Tab 3 顶部添加一键展开/折叠按钮：使用 `st.session_state["all_expanded"]` 布尔值控制，两个按钮"🔽 展开全部"和"🔼 折叠全部"通过 `st.columns(2)` 并排，点击后切换状态，传递给所有 expander 的 `expanded` 参数。
  - [x] SubTask 3.4：保留 Tab 3 原有的"算法选型结果"卡片和"DeepSeek 解释"区域不变。

- [x] Task 4（提示词 6-4）：升级 Tab 4 — 完整报告渲染、导出、人在回路面板
  - [x] SubTask 4.1：重写 Tab 4 报告渲染：将原来 10 个 `st.expander` 改为 10 个 `st.markdown` 区块，每个区块用 `st.divider()` 分隔。每个区块标题用 `###` 渲染，内容用 `st.markdown` 渲染 Markdown 格式。
  - [x] SubTask 4.2：在"实验结果"字段内嵌 Plotly 图表：如果 `st.session_state.benchmark_results` 存在，绘制柱状图（算法 vs 成功率）和雷达图（5 算法 × 10 维），用 `st.plotly_chart` 渲染。
  - [x] SubTask 4.3：实现"参考论文"字段的 DOI/URL 可点击链接：用正则 `r"(https?://[^\s]+)"` 匹配 URL 转换为 Markdown 链接，用正则匹配 DOI 转为 `https://doi.org/...` 链接。
  - [x] SubTask 4.4：新增 3 种导出按钮（`st.columns(3)` 横向排列）：
    - "📥 导出 Markdown 报告"：调用 `generate_markdown_report` 生成文字并 `st.download_button` 下载
    - "📥 导出 JSON 数据"：将完整 `st.session_state.decision` + `st.session_state.hypothesis` + `st.session_state.env_input` + `st.session_state.benchmark_results` 序列化为 JSON 供下载
    - "📥 导出实验数据 CSV"：从 `ExperimentDB` 查询实验记录，转为 CSV 供下载（try/except 包裹，数据库不可用时显示灰色禁用按钮+提示）
  - [x] SubTask 4.5：实现人在回路面板：当 `st.session_state.decision.get("need_human_check", False) == True` 或 ranking 前 2 名得分差 < 0.05 时，在 Tab 4 顶部用 `st.error("⚠️ AI 决策存在不确定性，请人工审核")` 显示红色 alert。
  - [x] SubTask 4.6：人在回路面板内提供"调整优化优先级"下拉菜单（`st.selectbox`，选项同 Tab 1）+ "质疑结论"输入框（`st.text_area`）+ "🔄 提交反馈并重新分析"按钮。点击后把反馈写入 `st.session_state.env_input["human_feedback"]` + 更新 `optimization_preference`，重新调用 `execute_decision_pipeline_v2`，然后 `st.rerun()`。

- [x] Task 5：整体收口 — 确保旧功能不被破坏
  - [x] SubTask 5.1：验证 `python -c "from gui.visualization import draw_grid, draw_ranking_bar, draw_radar, draw_10d_bar, draw_10d_radar, render_reasoning_chain; print('visualization imports OK')"` 通过 ✅
  - [x] SubTask 5.2：验证 `python -c "from gui.streamlit_app import main; print('streamlit_app imports OK')"` 通过（不启动 GUI，仅检查导入）✅
  - [x] SubTask 5.3：确保旧版 `execute_decision_pipeline` 函数保留不动，`execute_decision_pipeline_v2` 作为新增函数向前兼容，原有调用方不报错 ✅

# Task Dependencies

- Task 1（Tab 1 升级）独立，最先开始；依赖 `MapParser` 和 `BenchmarkLoader`（已有）✓
- Task 2（Tab 2 升级）依赖 Task 1 中新增的 `optimization_preference` / `grid_from_file` 传递链路（确保 Tab 2 能正确获取数据）；可与 Task 1 后半部分并行开发 ✓
- Task 3（Tab 3 升级）独立于 Tab 1/Tab 2，仅依赖 `decision` 和 `st.session_state` 现有数据；可与 Task 2 并行 ✓
- Task 4（Tab 4 升级）依赖 Task 1 的 `optimization_preference` 传递；可与 Task 2/Task 3 并行 ✓
- Task 5（整体收口）依赖 Task 1 ~ Task 4 全部完成 ✓

# 并行化建议

- Task 2 的 visualization.py 新函数（2.1/2.2）与 Task 3 的 visualization.py 改写（3.1）并行开发，通过 Agent A 统一处理 ✅
- Task 2 的 streamlit_app.py Tab 2 改造（2.3-2.8）与 Task 4 的 Tab 4 改造（4.1-4.6）修改同一文件不同区域，通过 Agent B 统一处理 ✅
- 实际分配：Agent A 负责 visualization.py 全部改动（Task 2.1/2.2/2.8 + Task 3.1/3.2），Agent B 负责 streamlit_app.py 全部改动（Task 1 + Task 2.3-2.7 + Task 3.3-3.4 + Task 4）✅
