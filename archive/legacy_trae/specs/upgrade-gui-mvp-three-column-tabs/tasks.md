# Tasks

- [x] Task 1: 更新依赖：在 `requirements.txt` 追加 `plotly>=5.15.0`
  - [x] SubTask 1.1: 打开 `ai_scientist_path_planning/requirements.txt` 核对是否已含 `plotly`，如未含则追加
  - [x] SubTask 1.2: 在项目根目录运行 `pip install -r ai_scientist_path_planning/requirements.txt`（或 `pip install plotly>=5.15.0`）确认无安装错误

- [x] Task 2: 准备后端依赖模块（按执行方案 §2.2 提示）
  - [x] SubTask 2.1: 检查 `ai_scientist_path_planning/map/map_analyzer.py` 是否已存在；若不存在则新建 `MapAnalyzer` 类（提供 `analyze(grid, start, target) -> dict`，含 `scene_level`、`complexity_index` 等键）
  - [x] SubTask 2.2: 检查 `ai_scientist_path_planning/agents/parameter_agent.py` 是否已存在；若不存在则新建 `ParameterAgent` 类（提供 `recommend(env_input, decision) -> dict`）
  - [x] SubTask 2.3: 跑一遍 `python -m pytest ai_scientist_path_planning/tests/ -q` 确认新增模块未破坏现有测试

- [x] Task 3: 扩展 `gui/visualization.py`（新增 6 个辅助函数，保持原 3 个函数签名不变）
  - [x] SubTask 3.1: 在文件顶部追加 `import plotly.graph_objects as go`（仅当实际使用时 import，避免破坏当前轻量依赖）
  - [x] SubTask 3.2: 新增 `draw_metric_cards(metrics: dict) -> go.Figure`，按执行方案 §5.2 占位实现（指标卡片组合图）
  - [x] SubTask 3.3: 新增 `draw_scene_indicator(scene_level: str, complexity: float) -> go.Figure`，按执行方案 §5.2 用 `go.Indicator(mode="gauge+number", ...)` 实现
  - [x] SubTask 3.4: 新增 4 个面向 Tab3/Tab4 的辅助：`render_decision_card(decision)`、`render_reasoning_chain(decision)`、`generate_markdown_report(hypothesis, decision, env_input) -> str`、`regenerate_hypothesis()`（其中 `render_decision_card` / `render_reasoning_chain` 因依赖 `st` 也可放在 `streamlit_app.py` 中，本任务先在 `visualization.py` 写好纯函数版 `generate_markdown_report`）
  - [x] SubTask 3.5: 保留原有 `draw_grid` / `draw_ranking_bar` / `draw_radar` 函数签名与逻辑不变

- [x] Task 4: 重写 `gui/streamlit_app.py` 为 4 Tab 布局
  - [x] SubTask 4.1: 顶部 `st.set_page_config(page_title=..., page_icon="🔬", layout="wide", initial_sidebar_state="collapsed")`
  - [x] SubTask 4.2: 在 `main()` 开头按执行方案 §3.2 写入 9 个 Session State 初始值
  - [x] SubTask 4.3: 创建 4 个 `st.tabs([...])`：地图参数 / 环境分析 / 智能体推理 / 研究报告
  - [x] SubTask 4.4: 实现 Tab1：`st.columns([1, 2, 1])` 三栏；左栏参数输入 + 高级 expander + 两个按钮；中栏地图预览；右栏参数摘要
  - [x] SubTask 4.5: 抽取并实现 `execute_decision_pipeline(...)`（含 `MapAnalyzer` 的 `try/except` 降级、连通性最多重试 5 次、`st.rerun()` 等）
  - [x] SubTask 4.6: 实现 Tab2：上方 `st.columns([1, 1])` 场景分析 + 柱状图；下方 `st.divider()` + `st.columns([1, 1])` 雷达图 + Benchmark 数据表
  - [x] SubTask 4.7: 实现 Tab3：左右两栏；左栏决策卡片（`render_decision_card`）、指标评分详情（5 个 `st.metric`）、Qwen 解释；右栏 7 步推理链（`render_reasoning_chain`）、推荐算法参数 `st.code` JSON
  - [x] SubTask 4.8: 实现 Tab4：10 段 `st.expander`；底部 3 列按钮（下载 Markdown / PDF 禁用 / 重新生成）；实现 `regenerate_hypothesis()` 回调

- [x] Task 5: 启动验证
  - [x] SubTask 5.1: 在 `ai_scientist_path_planning/` 目录执行 `streamlit run gui/streamlit_app.py`，确认无 import 错误
  - [x] SubTask 5.2: 浏览器打开页面，依次测试 4 个 Tab 的渲染（即便决策未跑通也要保证 Tab 切换与提示语正常）
  - [x] SubTask 5.3: 在 Tab1 设置参数后点击 `▶ 开始多智能体分析`，观察 `st.spinner` → `st.success` → `st.rerun` 流程
  - [x] SubTask 5.4: 完成后切到 Tab2 / Tab3 / Tab4 检查各项内容是否渲染；点击 `📥 下载 Markdown` 验证文件下载
  - [x] SubTask 5.5: 在 4 个 Tab 间反复切换，确认 Session State 数据保持一致

- [x] Task 6: 回归测试
  - [x] SubTask 6.1: 运行 `python -m pytest ai_scientist_path_planning/tests/ -q` 确认所有现有测试通过
  - [x] SubTask 6.2: 如有 lint / typecheck 工具（参考 README / pyproject），运行相关命令

# Task Dependencies
- Task 2 必须在 Task 4 之前完成（`streamlit_app.py` 依赖 `MapAnalyzer` / `ParameterAgent` 至少在缺失场景下能优雅降级）
- Task 1 必须在 Task 4 之前完成（Tab2 中 Plotly 图表依赖）
- Task 3 与 Task 4 中 `streamlit_app.py` 编写可并行（独立模块），但 `streamlit_app.py` 仍需 import 正确的函数名
- Task 5 依赖 Task 1、2、3、4 全部完成
- Task 6 与 Task 5 可并行（独立测试套件）

# 实施与验证记录
- pytest 全部 21 个测试通过（`21 passed in 0.36s`）
- MapAnalyzer / ParameterAgent smoke test 通过（5 种算法均返回合理参数）
- streamlit AppTest 启动通过：4 Tab / 2 按钮 / 6 slider / 1 radio / 5 number_input / 1 expander / 5 metric 均渲染
- 完整管线 AppTest 通过：点击 `▶ 开始多智能体分析` 后 decision=ACO / 中复杂度 / 0.7296, hypothesis 含 10 个标准字段, features.scene_level=中复杂度, 全部 Session State 键就位，无异常
- 已将 streamlit 服务进程停止
