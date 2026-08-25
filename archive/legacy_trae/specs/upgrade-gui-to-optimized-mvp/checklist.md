# 验收 Checklist

## A* 搜索分步接口
- [x] `astar.py` 新增 `search_with_steps(grid, start, target) -> dict`，返回 `frames / final_path / success / nodes_expanded`
- [x] 每帧含 `visited` 集合、`frontier` 集合、`current` 节点
- [x] 原 `AStar().search()` 签名与实现保持不变
- [x] `pytest tests/ -q` 24 个测试全部通过（21 原有 + 3 新增 `search_with_steps`）
- [x] 新增 3 个 `search_with_steps` 单元测试（可达 / 不可达 / 起点=终点）

## gui/animation.py（Phase 1.1）
- [x] 新建 `ai_scientist_path_planning/gui/animation.py`（192 行）
- [x] 导出 `create_search_animation(grid, algorithm, start, target) -> go.Figure`
- [x] A* 动画通过 `search_with_steps` 驱动，输出 Plotly `Frames` 序列（20×20 网格实测 302 帧）
- [x] ACO/PSO/SA 占位返回单帧（带提示）

## gui/visualization.py Plotly 化（Phase 1.4）
- [x] `draw_grid` 重写为 `go.Heatmap` + 起点/终点 `go.Scatter`，含 `hovertemplate`（签名不变）
- [x] `draw_ranking_bar` 重写为 `go.Bar` 含 `hovertemplate`（签名不变，修复了旧 `r["detail"]["time_score"]` bug）
- [x] `draw_radar` 重写为 `go.Scatterpolar` 含 `hovertemplate`（签名不变）
- [x] 函数签名不变（参数列表兼容）；返回类型从 `Figure(matplotlib)` 变 `Figure(plotly)`
- [x] smoke test 三个新函数均可被 `st.plotly_chart` 直接渲染

## 多路径同屏对比（Phase 1.2）
- [x] 新增 `draw_multi_path_overlay(grid, paths, start, target)`
- [x] 颜色映射 A*=#e74c3c / ACO=#3498db / PSO=#2ecc71 / SA=#f39c12 / 混合优化算法=#9b59b6
- [x] smoke test 验证 5 条路径不同颜色清晰可辨

## 指标下拉切换柱状图（Phase 1.3）
- [x] 新增 `draw_animated_bar_chart(ranking, metrics)`，默认 6 指标
- [x] Plotly `updatemenus` 下拉切换；切换时通过 `visible` 数组控制显隐
- [x] smoke test 验证 `updatemenus` 存在且 buttons 数量与 metrics 一致

## 10 维雷达图（Phase 2.1）
- [x] 新增 `draw_extended_radar(ranking, metrics_10=None)`
- [x] 默认 10 个 `*_score` 字段
- [x] 缺失字段默认填 0.0，不抛异常
- [x] smoke test 返回 `go.Figure`

## 增强推理链（Phase 2.10）
- [x] 新增 `render_enhanced_reasoning_chain(decision)`，每步含置信度
- [x] 展开后显示 input / output JSON
- [x] 提供"展开全部 / 折叠全部"按钮（session_state 控制）

## Pareto 前沿
- [x] 新增 `highlight_pareto_front(ranking)`，2 维散点（耗时 vs 路径长度）
- [x] 非支配点高亮，Pareto 最优集用红星标记
- [x] 空数据 / 缺字段安全返回空 Figure

## PDF 导出降级（Phase 2.11）
- [x] 新增 `export_pdf_or_fallback(md_content, file_name)` 返回 `(data, mime, fallback_used)` 三元组
- [x] `pdfkit` 缺失时降级为 Markdown 下载 + 警告提示
- [x] 不强制安装新依赖

## gui/streamlit_app.py 集成
- [x] 所有 `st.pyplot(fig)` 替换为 `st.plotly_chart(fig, use_container_width=True)`（draw_grid 调用点）
- [x] Tab1 中栏加"显示所有算法路径"复选框
- [x] Tab1 中栏加 A* 算法的"播放搜索过程"按钮（仅 best_algorithm=="A*" 时启用）
- [x] Tab2 上方右侧柱状图替换为 `draw_animated_bar_chart`
- [x] Tab2 下方左侧加 4维/10维单选按钮 + Pareto 前沿散点
- [x] Tab3 推理链替换为 `render_enhanced_reasoning_chain`
- [x] Tab4 底部"📥 导出 PDF 报告"按 `export_pdf_or_fallback` 降级策略
- [x] 原有 Tab1 文件上传 / 模板 / Benchmark loader / 人在回路 / 多导出格式 等所有功能保持不变

## 启动与运行
- [x] `streamlit run gui/streamlit_app.py` 启动无 import 错误（AppTest 启动通过）
- [x] 4 个 Tab 切换、Session State 数据保持一致
- [x] AppTest 模拟：点击"开始多智能体分析"后 decision=混合优化算法/中复杂度、grid / features / params / hypothesis 全部就位
- [x] Tab1 "显示所有算法路径" 复选框可见
- [x] Tab2 4维/10维 radio 可见；`draw_animated_bar_chart` 替代 `draw_ranking_bar`
- [x] Tab3 `render_enhanced_reasoning_chain` 替换 `render_reasoning_chain` 无异常
- [x] Tab4 4 列导出按钮（Markdown / JSON / CSV / PDF 降级）布局正常
- [x] 8 个 Plotly chart 实际渲染成功

## 回归测试
- [x] `python -m pytest ai_scientist_path_planning/tests/ -q` 全部通过（24 passed in 0.79s，含 3 个新增 `search_with_steps` 测试）
- [x] `draw_multi_path_overlay` / `draw_extended_radar` / `highlight_pareto_front` / `draw_animated_bar_chart` / `export_pdf_or_fallback` smoke test 全部通过
- [x] `animation.create_search_animation` 在 A* 网格上生成 302 帧动画，ACO/PSO/SA 占位返回单帧
