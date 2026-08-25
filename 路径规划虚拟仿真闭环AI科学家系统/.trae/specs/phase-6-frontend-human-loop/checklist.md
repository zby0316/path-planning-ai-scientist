# Checklist（Phase 6 前端展示与人在回路升级）

> 验证方法：每个条目在实现完成后由 Sub-Agent 或主流程实际执行/审阅，并通过在条目开头勾选 `[x]` 标记通过。

## Tab 1 — 文件上传、Benchmark 选择、模板按钮、优化偏好（提示词 6-1）

- [x] `st.file_uploader` 组件存在于 Tab 1，接受 `["csv", "json", "map", "scen", "npy"]` 类型
- [x] 上传 CSV 文件后，Tab 1 地图预览区域自动显示解析后的栅格地图
- [x] `st.selectbox` Benchmark 下拉菜单展示 `BenchmarkLoader().list_available_maps()` 返回的 9 个地图集名称
- [x] 选择 Benchmark 地图后，地图预览自动更新
- [x] 文件上传与 Benchmark 下拉互斥（上传文件后 Benchmark 被禁用，反之亦然）
- [x] 4 个模板按钮（低障碍/中障碍/高障碍/迷宫型）横向排列，点击后正确设置对应预设值
- [x] `st.radio` 优化偏好组件存在，4 个选项："耗时优先"、"成功率优先"、"路径最短"、"平衡模式"
- [x] 算力约束 radio 的 `help` tooltip 已增强说明
- [x] `execute_decision_pipeline_v2` 函数接收 `optimization_preference` 并写入 `env_input`
- [x] 上传/Benchmark 地图优先于随机生成地图展示
- [x] 旧版滑块参数（地图宽高/障碍物占比/连通性/拓扑随机性）保留可用

## Tab 2 — 10 维指标展示、Benchmark 对比、颜色编码（提示词 6-2）

- [x] `draw_10d_bar(detail)` 函数存在于 `gui/visualization.py`，返回 Plotly `go.Figure`
- [x] 10 维柱状图包含 10 个维度键名：`time_score` / `length_score` / `success_score` / `stability_score` / `smoothness_score` / `safety_score` / `expanded_nodes_score` / `compute_cost_score` / `robustness_score` / `penalty`
- [x] 10 维柱状图柱子颜色按阈值编码（≥0.8 绿、0.5~0.8 黄、<0.5 红）
- [x] `draw_10d_radar(ranking)` 函数存在于 `gui/visualization.py`，返回 Plotly `go.Figure`
- [x] 10 维雷达图显示 10 个轴和 5 条折线（5 个算法）
- [x] 原 4 维 matplotlib `draw_radar` 函数保留不动
- [x] Tab 2 展示障碍物聚类数、瓶颈通道数、分布熵 3 个指标卡片
- [x] Tab 2 展示 10 维指标评分柱状图
- [x] Tab 2 展示 Benchmark 实际运行结果对比表格（10 列），使用 `st.dataframe`
- [x] Tab 2 展示历史偏差提示（偏差 > 20% 时出现 `st.warning`）
- [x] `_score_color(score)` 辅助函数存在，正确返回 green/orange/red
- [x] 地图预览、场景等级、复杂度仪表盘保留可用

## Tab 3 — 12 智能体推理链卡片（提示词 6-3）

- [x] `render_reasoning_chain(decision, expanded_all)` 重写为 12 个智能体卡片（每个用 `st.expander`）
- [x] 12 个卡片分别对应：Data Agent / Map Analysis Agent / Environment Agent / Literature Agent / Knowledge Agent / Rule Agent / Evaluation Agent / Parameter Agent / Decision Agent / Hypothesis Agent / Reflection Agent / Human-Loop Agent
- [x] 每个卡片标题带有状态 emoji（🟢/🟡/🔴）
- [x] 每个卡片内部展示对应智能体的详细输出数据（非仅一行状态文字）
- [x] Tab 3 顶部"展开全部"/"折叠全部"按钮存在且功能正常
- [x] 原有"算法选型结果"卡片和"DeepSeek 解释"区域保留不变
- [x] 无数据/未执行的智能体卡片显示"未执行"状态而非报错

## Tab 4 — 完整报告渲染、导出、人在回路面板（提示词 6-4）

- [x] Tab 4 渲染完整 10 字段报告，使用 `st.markdown` + `st.divider()` 分隔
- [x] "实验结果"字段内嵌 Plotly 柱状图和雷达图（有数据时）
- [x] "参考论文"字段中 DOI 和 URL 渲染为可点击 Markdown 链接
- [x] 3 种导出按钮（Markdown / JSON / CSV）横向排列在报告底部
- [x] "📥 导出 Markdown 报告"按钮可下载 `.md` 文件
- [x] "📥 导出 JSON 数据"按钮可下载包含完整数据的 `.json` 文件
- [x] "📥 导出实验数据 CSV"按钮可下载实验记录 CSV（或数据库不可用时显示禁用+提示）
- [x] `need_human_check=True` 或得分差 < 0.05 时，Tab 4 顶部显示红色 `st.error` alert
- [x] 人在回路面板包含"调整优化优先级"下拉菜单
- [x] 人在回路面板包含"质疑结论"文本输入框
- [x] "提交反馈并重新分析"按钮功能正常：保存反馈 → 重新执行流水线
- [x] 无分析数据时 Tab 4 显示友好提示而非报错

## 整体收口

- [x] `python -c "from gui.visualization import draw_grid, draw_ranking_bar, draw_radar, draw_10d_bar, draw_10d_radar, render_reasoning_chain; print('visualization imports OK')"` 通过
- [x] `python -c "from gui.streamlit_app import main; print('streamlit_app imports OK')"` 通过（不启动 GUI，仅检查导入）
- [x] 旧版 `execute_decision_pipeline` 函数保留，旧调用方不报错
- [x] `python main.py` 正常运行（3 组场景输出排名详情）
- [x] `python -m pytest tests/ -v` 既有测试全部通过（21/21）
- [x] 所有新函数均有正确的类型注解和 docstring（使用中文）
