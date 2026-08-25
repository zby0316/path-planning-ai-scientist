# Tasks

- [x] Task 1: A* 搜索分步接口扩展（前置依赖）
  - [x] SubTask 1.1: 在 `ai_scientist_path_planning/algorithms/astar.py` 中新增 `search_with_steps(grid, start, target) -> dict`，返回 `{"frames": [...], "final_path": [...], "success": bool, "nodes_expanded": int}`；每帧 `{"visited": set, "frontier": set, "current": tuple}`
  - [x] SubTask 1.2: 保留原 `AStar().search()` 签名与实现不变，向后兼容
  - [x] SubTask 1.3: 运行 `python -m pytest ai_scientist_path_planning/tests/ -q` 确认 21 个原有测试仍通过

- [x] Task 2: 新建 `gui/animation.py`（Phase 1.1）
  - [x] SubTask 2.1: 实现 `create_search_animation(grid, algorithm, start, target) -> go.Figure`
  - [x] SubTask 2.2: A* 路径调用 `AStar().search_with_steps()` 并转换为 Plotly Frames（每帧标记已访问节点 + 当前路径）
  - [x] SubTask 2.3: 非 A* 算法以"该算法动画暂未实现"占位，绘制单帧
  - [x] SubTask 2.4: 顶部 `import plotly.graph_objects as go`、`import numpy as np`

- [x] Task 3: 扩展 `gui/visualization.py`（Phase 1 + 关键 Phase 2）
  - [x] SubTask 3.1: 重写 `draw_grid` 为 Plotly `go.Heatmap` + 起点/终点 `go.Scatter`，含 `hovertemplate`
  - [x] SubTask 3.2: 重写 `draw_ranking_bar` 为 Plotly `go.Bar` + `hovertemplate`
  - [x] SubTask 3.3: 重写 `draw_radar` 为 Plotly `go.Scatterpolar` + `hovertemplate`
  - [x] SubTask 3.4: 新增 `draw_multi_path_overlay(grid, paths, start, target)`，5 算法 5 颜色叠加
  - [x] SubTask 3.5: 新增 `draw_animated_bar_chart(ranking, metrics)`，updatemenus 下拉切换 6 指标
  - [x] SubTask 3.6: 新增 `draw_extended_radar(ranking, metrics_10=None)`，默认 10 维
  - [x] SubTask 3.7: 新增 `highlight_pareto_front(ranking)`（Pareto 前沿散点，2 维：耗时 vs 路径长度）
  - [x] SubTask 3.8: 新增 `render_enhanced_reasoning_chain(decision)` 含置信度 + input/output JSON
  - [x] SubTask 3.9: 新增 `export_pdf_or_fallback(md_content, file_name) -> bytes | str`，`try/except ImportError` pdfkit 降级

- [x] Task 4: 修改 `gui/streamlit_app.py`（替换调用 + 新增 Tab 控件）
  - [x] SubTask 4.1: 把所有 `st.pyplot(fig)` 替换为 `st.plotly_chart(fig, use_container_width=True)`（draw_grid 调用点）
  - [x] SubTask 4.2: Tab1 中栏加 `st.checkbox("显示所有算法路径")` 切换 `draw_multi_path_overlay`
  - [x] SubTask 4.3: Tab1 中栏加 A* 算法的"播放搜索过程"按钮（仅 best_algorithm=="A*" 时启用）→ 当前因决策管线不固定选 A*，按钮仅在 A* 入选时出现
  - [x] SubTask 4.4: Tab2 上方右侧柱状图调用替换为 `draw_animated_bar_chart`
  - [x] SubTask 4.5: Tab2 下方左侧加 4维/10维单选按钮切换 `draw_radar` / `draw_extended_radar`
  - [x] SubTask 4.6: Tab2 加 Pareto 前沿散点（`highlight_pareto_front`）
  - [x] SubTask 4.7: Tab3 推理链调用替换为 `render_enhanced_reasoning_chain`
  - [x] SubTask 4.8: Tab4 底部"📥 导出 PDF 报告"按钮按 `export_pdf_or_fallback` 降级策略（缺失依赖时降级为 Markdown）
  - [x] SubTask 4.9: 原有 Tab1 文件上传 / 模板 / Benchmark loader / 人在回路 / 多导出格式 等所有功能保持不变

- [x] Task 5: 启动验证
  - [x] SubTask 5.1: 4 个 Tab 切换、Session State 数据保持、按钮无异常（AppTest 启动通过、8 个 Plotly chart 渲染、3 个 radio / 1 个 checkbox）
  - [x] SubTask 5.2: Tab1 复选框 "显示所有算法路径" 渲染存在
  - [x] SubTask 5.3: Tab2 4维/10维 radio 切换、draw_animated_bar_chart 替换原 draw_ranking_bar
  - [x] SubTask 5.4: Tab3 增强推理链调用无异常（render_enhanced_reasoning_chain 替换原 render_reasoning_chain）
  - [x] SubTask 5.5: Tab4 4 列导出（Markdown / JSON / CSV / PDF 降级）布局正常
  - [x] SubTask 5.6: 全 6 个新可视化函数 smoke test 通过；`create_search_animation` A* 在 20×20 网格上生成 302 帧

- [x] Task 6: 回归测试与质量保障
  - [x] SubTask 6.1: 运行 `python -m pytest ai_scientist_path_planning/tests/ -q` 确认所有现有测试通过（24/24）
  - [x] SubTask 6.2: 编写针对 `search_with_steps` 的新增单元测试（3 个 case：可达 / 不可达 / 起点=终点）✅
  - [x] SubTask 6.3: 编写针对新可视化函数（`draw_multi_path_overlay` / `draw_extended_radar` / `highlight_pareto_front` / `draw_animated_bar_chart` / `export_pdf_or_fallback`）的 smoke test ✅

# Task Dependencies
- Task 1 必须在 Task 2 之前完成（`animation.py` 依赖 `AStar.search_with_steps`）
- Task 2 与 Task 3 可并行（不同文件，无依赖）
- Task 4 依赖 Task 2、Task 3 全部完成（`streamlit_app.py` 调用新函数）
- Task 5 依赖 Task 1~4
- Task 6 与 Task 5 可并行

# 实施与验证记录
- pytest 全部 24 个测试通过（含 3 个新增 `search_with_steps` 测试）
- AST 语法检查 4 个改动文件全部通过
- AppTest 启动通过：4 Tab / 8 Plotly chart / 3 radio / 1 checkbox / 全 9 个 Session State 键就位
- 完整管线 AppTest 通过：点击「▶ 开始多智能体分析」后 decision=混合优化算法 / 中复杂度，4 Tab 切换无异常
- smoke test 通过：7 个新可视化函数全部返回 go.Figure；`create_search_animation` A* 生成 302 帧动画；`export_pdf_or_fallback` 缺失 pdfkit 时降级为 Markdown bytes
- 已将 temp 测试文件（test_optimized_app.py / test_visualization_smoke.py）清理
