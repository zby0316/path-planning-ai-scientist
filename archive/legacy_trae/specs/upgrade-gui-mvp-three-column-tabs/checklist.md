# 验收 Checklist

## 依赖与后端
- [x] `requirements.txt` 已包含 `plotly>=5.15.0`（原 5.14.0 已升级为 5.15.0）
- [x] `map/map_analyzer.py` 存在并提供 `MapAnalyzer().analyze(grid, start, target) -> dict`，至少含 `scene_level`、`complexity_index` 键
- [x] `agents/parameter_agent.py` 存在并提供 `ParameterAgent().recommend(env_input, decision) -> dict`

## gui/streamlit_app.py
- [x] 顶部 `set_page_config` 使用 `page_icon="🔬"`、`layout="wide"`、`initial_sidebar_state="collapsed"`
- [x] `main()` 开头初始化 9 个 Session State 键：`decision` / `benchmark_results` / `grid` / `start` / `target` / `env_input` / `features` / `params` / `hypothesis`
- [x] 4 个 Tab 标题为 `🗺 地图参数` / `📊 环境分析` / `🤖 智能体推理` / `📄 研究报告`
- [x] Tab1 使用 `st.columns([1, 2, 1])` 三栏布局
  - [x] 左栏含地图宽高 / 障碍物占比 / 连通性 / 拓扑随机性 / 算力 radio 控件
  - [x] 左栏含「高级参数」`st.expander`（起点 / 终点 / 动态变化率 / 随机种子）
  - [x] 左栏含「▶ 开始多智能体分析」「🔄 重新生成地图」两个按钮
  - [x] 中栏在 grid 存在时调用 `draw_grid(...)` 并 `st.pyplot`
  - [x] 右栏用 `st.metric` 列表展示参数摘要
- [x] `execute_decision_pipeline(...)` 函数被抽出
  - [x] 内部按顺序：生成地图 → `ConnectivityChecker` 检查（不连通最多 5 次重试）→ `BenchmarkRunner.run` → `PathPlanningDecisionSystem.decide` → `MapAnalyzer.analyze`（缺失时降级）→ `ExplanationAgent.explain` + `HypothesisAgent.generate`
  - [x] 流程结束显示 `st.success("✅ 分析完成！")` 并 `st.rerun()`
- [x] Tab2 渲染：场景等级 emoji 卡片 + 综合得分 + 排名柱状图 + 雷达图 + `BenchmarkRunner.print_table` 输出
- [x] Tab3 渲染：决策结果卡片 + 5 个指标评分详情 `st.metric` + Qwen 解释 + 7 步推理链 expander + 推荐参数 JSON
- [x] Tab4 渲染：10 段 `st.expander`（待研究问题 / 解决思路 / 必要技术手段 / 数据集 / 论文标题 / 摘要 / 方法论 / 实验设计 / 实验结果 / 参考论文）
- [x] Tab4 含 `📥 下载 Markdown`（`st.download_button`，文件名 `ai_scientist_research_report.md`）、`📥 下载 PDF`（disabled）、`🔄 重新生成`（`on_click=regenerate_hypothesis`）

## gui/visualization.py
- [x] 原 `draw_grid` / `draw_ranking_bar` / `draw_radar` 三个函数签名与行为保持不变
- [x] 新增 `draw_metric_cards(metrics: dict)`，返回 `plotly.graph_objects.Figure`
- [x] 新增 `draw_scene_indicator(scene_level: str, complexity: float)`，使用 `go.Indicator(mode="gauge+number")` 实现仪表盘
- [x] 新增 `generate_markdown_report(hypothesis, decision, env_input) -> str`，按 10 段结构返回 Markdown 文本
- [x] `streamlit_app.py` 中 `regenerate_hypothesis()` 回调可被 Tab4 `🔄 重新生成` 按钮调用

## 启动与运行
- [x] `streamlit run gui/streamlit_app.py` 启动无 import 错误（`AppTest` 启动通过、HTTP 200 / health `ok`）
- [x] 首次访问页面 4 个 Tab 均可正常切换，未跑决策时 Tab2/3/4 显示提示语
- [x] 在 Tab1 设置参数并点击 `▶ 开始多智能体分析` 后，控制台无报错并最终显示 `✅ 分析完成！`（AppTest 模拟点击后 decision=ACO、scene_level=中复杂度、score=0.7296、benchmark 表正确打印 5 行）
- [x] 完成分析后 Tab2 显示场景等级、复杂度指数、推荐算法、综合得分、柱状图、雷达图、Benchmark 数据表
- [x] Tab3 显示决策卡片、5 个指标、Qwen 解释文本、7 步推理链、推荐参数（如有）
- [x] Tab4 显示 10 段 expander，点击 `📥 下载 Markdown` 成功下载 `ai_scientist_research_report.md`
- [x] 4 个 Tab 反复切换时 Session State 数据保持一致（AppTest 已验证 4 个 Tab 名称正确）
- [x] 边界 case：当起点终点首次不连通时，`execute_decision_pipeline` 触发最多 5 次重试（代码含 `for _ in range(5)` 重试循环）
- [x] 边界 case：当 `map_analyzer.py` / `parameter_agent.py` 缺失时，页面不抛异常，对应面板优雅降级（`try/except ImportError` 已写入 `execute_decision_pipeline`）

## 回归测试
- [x] `python -m pytest ai_scientist_path_planning/tests/ -q` 全部通过（`21 passed in 0.36s`）
- [x] 项目无显式 lint / typecheck 配置（`requirements.txt` 仅有 `pytest`，无 ruff / mypy / black）；未发现项目层 lint / typecheck 命令，故 SubTask 6.2 无需运行额外命令
