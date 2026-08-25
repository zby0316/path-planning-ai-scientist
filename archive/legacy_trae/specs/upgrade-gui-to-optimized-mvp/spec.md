# 优化版 MVP GUI 升级 Spec

## Why
基础版 GUI（`upgrade-gui-mvp-three-column-tabs`）已实现 4 Tab 三栏布局，但所有图表仍为 Matplotlib 静态图，且 Tab 间功能"展示有余、交互不足"，无法支持赛中展示与赛后迭代需要。`08-优化版MVP GUI搭建执行方案.md` 提出了 3 阶段渐进式升级（Phase 1 视觉交互、Phase 2 功能扩展、Phase 3 高级特性）。本变更以方案为依据，**优先实现 Phase 1 全量 + Phase 2 中 P0/P1 高价值项**，并以新增的 `gui/animation.py` 与 Plotly 化为主线，让 GUI 从"能跑"升级为"可演示"。

> **范围说明**：本 Spec 集中于"本次可落地"的 Phase 1 + 关键 Phase 2 项。Phase 3 高级特性（3D 体素、审稿人 Agent、ML 预测器、Docker、文献检索、LaTeX 等）属于 Phase 3 高风险范围，需独立 Spec，本 Spec 仅在末尾"未来工作"中列出占位说明。

## What Changes
- **新增** `gui/animation.py`：搜索过程动画生成器（`create_search_animation`），输出 Plotly `Frames` 动画。
- **扩展** `gui/visualization.py`：
  - **Plotly 重写** 3 个原 Matplotlib 函数：`draw_grid` / `draw_ranking_bar` / `draw_radar`，返回 `go.Figure`，支持悬停提示与图例交互。
  - **新增** 5 个 Phase 1 函数：`draw_multi_path_overlay`（多路径同屏对比）、`draw_animated_bar_chart`（指标下拉切换）、`draw_extended_radar`（10 维雷达图）、`highlight_pareto_front`（Pareto 前沿散点）、`draw_faceted_comparison`（分面对比占位）。
  - **新增** 1 个 Phase 2 辅助：`generate_lite_pdf`（无 pdfkit 依赖的纯 Python PDF 降级导出为可选）。`pdfkit` 导出作为可选升级，缺失时给出友好提示。
- **修改** `gui/streamlit_app.py`：
  - Tab1 中栏地图预览调用 `draw_grid`（Plotly 版），并在地图区下方加"显示所有算法路径"复选框（绑定 `draw_multi_path_overlay`）；左栏加"地图预设模板"下拉（5 套模板自动填滑块），加"上传地图文件"上传组件（CSV/JSON 解析）。
  - Tab2 上方两栏：`draw_ranking_bar` → `draw_animated_bar_chart`（保留 `draw_ranking_bar` 作为兼容 fallback）；下方左：增加"4 维 / 10 维"切换控件，调用 `draw_radar` 或 `draw_extended_radar`；下方右：保留 Benchmark 数据表。
  - Tab3 推理链：增加"展开/折叠全部"与"显示置信度"开关；调用新版本 `render_reasoning_chain` 增强版（含置信度）。
  - Tab4 底部 3 列按钮：把"下载 PDF"从 disabled 改为可点击（按 PDF 导出能力降级策略：若 `pdfkit` 可用 → 导出 PDF；否则 → 提示 + 仍可下载 Markdown）。
  - 不删除任何已有函数；所有 Plotly 旧函数保留为兼容版本。
- **不修改** `algorithms/*` / `evaluation/*` / `agents/*` / `map/*` 后端模块逻辑（10 维指标已由 `evaluation/metrics.py` 提供，ranking 详情中 `detail` 字典已含 10 维 `_score` 字段）。
- **不新增** pip 依赖（Plotly 已在基础版引入；`pdfkit` / `streamlit-drawable-canvas` 等作为可选增强，缺失时优雅降级）。

## Impact
- Affected specs: GUI 展示层（Tab1 地图 / Tab2 图表 / Tab3 推理链 / Tab4 报告）。
- Affected code:
  - `ai_scientist_path_planning/gui/visualization.py`（Matplotlib→Plotly 重写 + 新增函数）
  - `ai_scientist_path_planning/gui/animation.py`（新建）
  - `ai_scientist_path_planning/gui/streamlit_app.py`（替换图表调用 / 新增 Tab 控件）
- 受影响上下游：
  - `streamlit_app.py` 调用 Plotly 版 `draw_grid / draw_ranking_bar / draw_radar` 时使用 `st.plotly_chart(fig, use_container_width=True)` 替代 `st.pyplot(fig)`。
  - `animation.py` 仅依赖 Plotly + numpy；A* 搜索动画需在 `astar.py` 中扩展"逐步帧"接口（见下方 ADDED Requirements）。
  - 10 维雷达图通过 `ranking[i]["detail"]` 已含的 `time_score / length_score / success_score / stability_score / smoothness_score / safety_score / expanded_nodes_score / compute_cost_score / robustness_score` 等字段渲染，无需改后端。

## ADDED Requirements

### Requirement: 图表 Plotly 化（Phase 1.4）
`gui/visualization.py` 中的 `draw_grid` / `draw_ranking_bar` / `draw_radar` 必须重写为返回 `plotly.graph_objects.Figure`，支持 `hovertemplate` 悬停提示与图例点击切换。
- `draw_grid` 使用 `go.Heatmap` 或 `go.Scatter` 渲染栅格。
- `draw_ranking_bar` 使用 `go.Bar` 含 `hovertemplate` 显示具体分数。
- `draw_radar` 使用 `go.Scatterpolar` 含 `hovertemplate`。
- **向后兼容**：原 3 个 Matplotlib 函数体可保留（注释为旧版），新版本为同名 Plotly 实现，签名不变。

#### Scenario: 图表悬停交互
- **WHEN** 用户在 Tab2 鼠标悬停在排名柱状图的某条柱上
- **THEN** Plotly tooltip 显示算法名 + 综合得分（保留 4 位小数）

#### Scenario: 图例点击切换
- **WHEN** 用户在 Tab2 多指标雷达图中点击某算法图例
- **THEN** 该算法的轨迹在雷达图中隐藏，再次点击恢复

### Requirement: 多路径同屏对比（Phase 1.2）
新增 `draw_multi_path_overlay(grid, paths: dict, start, target)`，输入 `{"A*": [(x,y),...], "ACO": [...], ...}`，使用 5 种固定颜色叠加绘制。
- 颜色映射：`A*=#e74c3c, ACO=#3498db, PSO=#2ecc71, SA=#f39c12, 混合优化算法=#9b59b6`。
- 起点 / 终点用绿色 / 红色 marker 高亮。

#### Scenario: 同时显示 5 种算法路径
- **WHEN** Tab1 中栏"显示所有算法路径"复选框被勾选
- **THEN** 中栏地图区使用 `draw_multi_path_overlay` 渲染 5 条不同颜色的路径；未勾选时仅显示当前最优路径（由 `draw_grid` 渲染）

### Requirement: 指标下拉切换柱状图（Phase 1.3）
新增 `draw_animated_bar_chart(ranking: list, metrics: list)`，使用 `go.Bar` + Plotly `updatemenus` 下拉菜单在不同指标维度间切换。
- 默认 metrics 列表 = `["time", "length", "success", "stability", "smoothness", "safety"]`。
- 下拉按钮的 label 与 `metrics` 一一对应；切换时通过 `visible` 数组控制显隐。

#### Scenario: 切换指标维度
- **WHEN** 用户在 Tab2 排名柱状图右上角下拉菜单中点击"路径长度"
- **THEN** 所有柱形按 `length_score` 重绘，其他指标柱形隐藏

### Requirement: 路径搜索动画（Phase 1.1）
**新增** `gui/animation.py`，含 `create_search_animation(grid, algorithm: str, start, target) -> go.Figure`。
- A* 动画：返回 Plotly `Frames` 序列，每一帧展示当前 `closed set` 边界（已访问节点）与最终路径逐渐浮现。
- A* 的"逐步帧"由 `astar.py` 新增 `search_with_steps(grid, start, target) -> dict` 提供，返回 `{"frames": [{"visited": set, "path": [...]}, ...], "final_path": [...]}`。该方法在 `astar.py` 中以独立方法新增，不替换原 `search`。
- ACO/PSO 动画暂以占位实现（A* 即可满足"搜索动画可播放"验收，其余算法以"未实现"提示）。

#### Scenario: 播放 A* 搜索动画
- **WHEN** 用户在 Tab1 中栏点击"播放搜索过程"按钮（仅 A* 算法）
- **THEN** 地图区下方出现 Plotly 动画组件，点击 ▶ 后逐帧展示节点访问与最终路径

### Requirement: 10 维雷达图（Phase 2.1）
新增 `draw_extended_radar(ranking: list, metrics_10: list = None) -> go.Figure`。
- 默认 `metrics_10 = ["time_score", "length_score", "success_score", "stability_score", "smoothness_score", "safety_score", "expanded_nodes_score", "compute_cost_score", "robustness_score", "path_length_score"]`。
- 缺失字段默认填 0.0，不抛异常。

#### Scenario: 切换 4 维 / 10 维
- **WHEN** 用户在 Tab2 雷达图区域切换 "4 维 / 10 维" 单选按钮
- **THEN** 雷达图按 4 维或 10 维重绘

### Requirement: 地图预设模板（Phase 2.6）
在 Tab1 左栏加 `MAP_TEMPLATES` 下拉选择器，5 套模板：
```python
MAP_TEMPLATES = {
    "迷宫型": {"obstacle_ratio": 0.45, "connectivity": 0.30, "topology_randomness": 0.20},
    "空旷型": {"obstacle_ratio": 0.10, "connectivity": 0.90, "topology_randomness": 0.50},
    "窄通道型": {"obstacle_ratio": 0.55, "connectivity": 0.25, "topology_randomness": 0.30},
    "岛链型": {"obstacle_ratio": 0.35, "connectivity": 0.40, "topology_randomness": 0.80},
    "密集障碍": {"obstacle_ratio": 0.75, "connectivity": 0.15, "topology_randomness": 0.60},
}
```
选中模板时自动设置障碍物占比 / 连通性 / 拓扑随机性 3 个 slider 的 value（通过 `st.session_state[key]` 配合回调实现）。

#### Scenario: 选择"迷宫型"模板
- **WHEN** 用户在 Tab1 左栏"快速模板"下拉中选择"迷宫型"
- **THEN** `obstacle_ratio=0.45` / `connectivity=0.30` / `topology_randomness=0.20` 自动填入对应 slider

### Requirement: 地图文件上传（Phase 2.8）
在 Tab1 左栏加 `st.file_uploader("上传地图文件", type=["csv", "json"])`。
- CSV：使用 `np.loadtxt` 解析为 0/1 整型 grid。
- JSON：解析为 `{"grid": [[...]]}` 格式。
- 上传成功后 `st.session_state.uploaded_grid` 被填充，按钮区显示"使用上传地图"按钮；点击后把 uploaded_grid 写入 `st.session_state.grid` 替代随机生成。

#### Scenario: 上传 JSON 地图
- **WHEN** 用户上传 100×100 的 JSON 文件 `{"grid": [[0,1,0,...], ...]}`
- **THEN** "使用上传地图"按钮变为可用；点击后 `st.session_state.grid` 被替换为上传的 grid，地图预览重绘

### Requirement: 增强推理链（Phase 2.10）
新增 `render_enhanced_reasoning_chain(decision: dict)`，在原 `render_reasoning_chain` 基础上增加：
- 每个 expander 标题含置信度（如"① 数据接收智能体  置信度 100%"）。
- 展开后显示该步骤 input / output JSON（`st.json` 形式）。
- 顶部"展开全部 / 折叠全部"按钮。

#### Scenario: 展开推理链详情
- **WHEN** 用户在 Tab3 推理链区域点击"② 环境分析智能体"
- **THEN** expander 展开后显示该步骤的输入（如 `env_input`）与输出（如 `{"scene_level": "中复杂度"}`）JSON

### Requirement: PDF 导出降级（Phase 2.11）
Tab4 底部"📥 下载 PDF"按钮逻辑：
- 尝试 `import pdfkit`，若成功则调用 `export_pdf(md_content, file_name)` 生成 PDF。
- 失败时显示 `st.warning("PDF 导出依赖 pdfkit + wkhtmltopdf 未安装，已降级为 Markdown 下载。")` 并仍可下载 Markdown。
- 不强制安装新依赖。

#### Scenario: 缺少 pdfkit 时下载
- **WHEN** 用户在 Tab4 点击"📥 下载 PDF"，环境中未安装 pdfkit
- **THEN** 页面显示警告，按钮实际触发 Markdown 下载（fallback）；不抛异常

## MODIFIED Requirements

### Requirement: 现有图表函数（兼容性）
**MODIFIED**：原 `draw_grid` / `draw_ranking_bar` / `draw_radar` 实现从 Matplotlib 迁移到 Plotly。
- 函数签名不变（参数列表保持向后兼容）。
- 返回类型从 `matplotlib.figure.Figure` 变为 `plotly.graph_objects.Figure`。
- 现有调用方 `streamlit_app.py` 中所有 `st.pyplot(fig)` 必须改为 `st.plotly_chart(fig, use_container_width=True)`。

### Requirement: Tab1 中栏地图区（增强）
**MODIFIED**：Tab1 中栏从单一 `draw_grid` 升级为：
- 上半：地图预览（Plotly `draw_grid`）。
- 下半：复选框"显示所有算法路径"控制是否叠加 `draw_multi_path_overlay`。
- 复选框右侧：A* 算法的"播放搜索过程"按钮（仅当 `algorithm == "A*"` 时启用）。

### Requirement: Tab2 排名柱状图（升级）
**MODIFIED**：原 `draw_ranking_bar` 替换为 `draw_animated_bar_chart`，支持下拉切换 6 个指标。

### Requirement: Tab2 雷达图（维度扩展）
**MODIFIED**：Tab2 雷达图区域增加 "4 维 / 10 维" 单选按钮，按选择调用 `draw_radar` 或 `draw_extended_radar`。

### Requirement: Tab4 下载按钮（PDF 降级）
**MODIFIED**：原 Tab4 `📥 下载 PDF` 按钮从 `disabled=True` 改为按 `pdfkit` 可用性动态启用；`help` 文案更新为"PDF 导出依赖 pdfkit，未安装时降级为 Markdown 下载"。

## REMOVED Requirements
（无：基础版所有函数与控件均保留；本次升级以"叠加 / 升级"为主，不删除任何已有代码路径。）

---

# 附录：Phase 3 未来工作（占位说明，不在本 Spec 实施范围）

| 阶段 | 模块 / 文件 | 说明 |
|------|------------|------|
| Phase 3.1 | `gui/threejs_renderer.py` | Three.js 3D 体素地图 |
| Phase 3.2 | Tab3 多智能体辩论 | 持不同观点智能体对话气泡 |
| Phase 3.3 | Tab3 多轮对话 | `st.chat_input` 与 `HumanLoopAgent` 接入 |
| Phase 3.4 | 敏感度分析 | 权重 ±delta 扫描 |
| Phase 3.5 | 权重拖拽实时重算 | `st.slider(on_change=recalculate)` |
| Phase 3.6 | LaTeX 论文导出 | `generate_latex_paper` |
| Phase 3.7 | 文献检索 | Semantic Scholar API |
| Phase 3.8 | 审稿人 Agent | `agents/reviewer_agent.py` |
| Phase 3.9 | Docker 部署 | `Dockerfile` |
| Phase 3.10 | ML 性能预测 | `evaluation/predictor.py` |
| Phase 3.11 | 实验闭环 | `auto_experiment_loop` |
| Phase 3.12 | 多机器人协同 | `draw_multi_robot_paths` |

后续可按需拆分为独立 Spec 实施。
