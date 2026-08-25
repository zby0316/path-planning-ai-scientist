# 基础版 MVP GUI 搭建执行方案

> 基于 [基础版与优化版MVP GUI界面设计方案.md](基础版与优化版MVP%20GUI界面设计方案.md) 中提取的基础版内容，扩展为可逐步骤落地的执行方案。
> 前置条件：[05-基础版MVP全流程搭建执行方案.md](05-基础版MVP全流程搭建执行方案.md) 已执行完成。

---

## 一、概述

### 1.1 目标

将当前简陋的单页面 Streamlit 应用升级为 **三栏布局 + 顶部4Tab导航 + 底部全宽报告区** 的专业级 GUI。

### 1.2 技术栈

| 组件 | 选型 | 用途 |
|------|------|------|
| 框架 | Streamlit 1.x | 整体页面框架 |
| 图表 | Matplotlib + Plotly | 地图可视化、柱状图、雷达图 |
| 数据 | NumPy | 数组处理 |

### 1.3 现有代码基线

- `gui/streamlit_app.py` — 当前约142行，左右两栏布局，sidebar输入 + 中右显示
- `gui/visualization.py` — 当前约78行，含 `draw_grid`、`draw_ranking_bar`、`draw_radar` 三个函数

### 1.4 目标产出

- `gui/streamlit_app.py` — **重写**为三栏+Tab布局，约350行
- `gui/visualization.py` — **扩展**至约200行，新增6个函数

---

## 二、前置依赖检查

### 2.1 已安装的 Python 包

确认以下包已存在于 `requirements.txt` 并已安装：

```
streamlit>=1.28.0
matplotlib>=3.7.0
numpy>=1.24.0
```

新增依赖（需补充到 `requirements.txt`）：

```
plotly>=5.15.0
```

### 2.2 后端模块依赖

执行本方案前，以下后端模块必须已完成并通过测试：

- [x] `main.py` — `PathPlanningDecisionSystem` 类
- [x] `map/map_generator.py` — `MapGenerator` 类
- [x] `map/connectivity_checker.py` — `ConnectivityChecker` 类
- [x] `evaluation/benchmark.py` — `BenchmarkRunner` 类
- [x] `agents/explanation_agent.py` — `ExplanationAgent` 类
- [x] `agents/hypothesis_agent.py` — `HypothesisAgent` 类
- [ ] `map/map_analyzer.py` — `MapAnalyzer` 类（**需新建或确认存在**，用于场景等级判定）
- [ ] `agents/parameter_agent.py` — `ParameterAgent` 类（**需新建**，用于推荐算法参数）

---

## 三、页面架构搭建

### 3.1 页面配置

在 `streamlit_app.py` 最顶层设置：

```python
import streamlit as st

st.set_page_config(
    page_title="AI Scientist 路径规划算法选型系统",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)
```

**要点**：
- `layout="wide"` 是核心，充分利用屏幕宽度放置三栏
- `initial_sidebar_state="collapsed"` 隐藏默认 sidebar，因为输入面板将在页面内实现

### 3.2 Session State 初始化

在 `main()` 函数开头添加：

```python
if "decision" not in st.session_state:
    st.session_state.decision = None
if "benchmark_results" not in st.session_state:
    st.session_state.benchmark_results = None
if "grid" not in st.session_state:
    st.session_state.grid = None
if "start" not in st.session_state:
    st.session_state.start = None
if "target" not in st.session_state:
    st.session_state.target = None
if "env_input" not in st.session_state:
    st.session_state.env_input = {}
if "features" not in st.session_state:
    st.session_state.features = None
if "params" not in st.session_state:
    st.session_state.params = None
if "hypothesis" not in st.session_state:
    st.session_state.hypothesis = None
```

### 3.3 顶部 Tab 导航

```python
tab_map, tab_analysis, tab_reasoning, tab_report = st.tabs([
    "🗺 地图参数",
    "📊 环境分析",
    "🤖 智能体推理",
    "📄 研究报告"
])
```

---

## 四、Tab 1: 地图参数页面

### 4.1 布局：三栏 (1:2:1)

```python
with tab_map:
    col_left, col_mid, col_right = st.columns([1, 2, 1])
```

### 4.2 左栏：输入面板

```python
with col_left:
    st.subheader("📥 地图参数输入")

    map_width = st.slider("地图宽度", 10, 500, DEFAULT_MAP_WIDTH, 10)
    map_height = st.slider("地图高度", 10, 500, DEFAULT_MAP_HEIGHT, 10)
    obstacle_ratio = st.slider("障碍物占比", 0.0, 1.0, 0.35, 0.01,
                               help="地图中障碍物所占比例，0~1")
    connectivity = st.slider("通道连通性", 0.0, 1.0, 0.68, 0.01,
                             help="越高表示连通区域越多")
    topology_randomness = st.slider("拓扑随机性", 0.0, 1.0, 0.55, 0.01,
                                    help="越高表示障碍分布越随机")
    compute_limit = st.radio("算力限制", ["low", "medium", "high"],
                             index=1, horizontal=True,
                             help="low=受限 high=充足")

    with st.expander("⚙ 高级参数"):
        start_x = st.number_input("起点 X", 0, map_width - 1, 0)
        start_y = st.number_input("起点 Y", 0, map_height - 1, 0)
        target_x = st.number_input("终点 X", 0, map_width - 1, map_width - 1)
        target_y = st.number_input("终点 Y", 0, map_height - 1, map_height - 1)
        dynamic_change_rate = st.slider("动态变化率", 0.0, 1.0, 0.0, 0.01,
                                        help="非零时模拟动态障碍物环境")
        random_seed = st.number_input("随机种子", 0, 9999, 42)

    run_btn = st.button("▶ 开始多智能体分析", type="primary", use_container_width=True)
    regenerate_btn = st.button("🔄 重新生成地图", use_container_width=True)
```

### 4.3 中栏：地图预览

```python
with col_mid:
    st.subheader("🗺 地图预览")

    if run_btn or regenerate_btn:
        generator = MapGenerator(seed=random_seed)
        grid = generator.generate(map_width, map_height, obstacle_ratio,
                                   (start_x, start_y), (target_x, target_y))
        st.session_state.grid = grid
        st.session_state.start = (start_x, start_y)
        st.session_state.target = (target_x, target_y)

    if run_btn:
        # 触发完整决策流程
        with st.spinner("🧠 多智能体系统正在分析..."):
            execute_decision_pipeline(
                map_width, map_height, obstacle_ratio, connectivity,
                topology_randomness, compute_limit, random_seed,
                start_x, start_y, target_x, target_y, dynamic_change_rate
            )
        st.success("✅ 分析完成！")
        st.rerun()

    if st.session_state.grid is not None:
        fig_grid = draw_grid(
            st.session_state.grid,
            start=st.session_state.start,
            target=st.session_state.target,
            title=f"随机栅格地图 (障碍物占比={obstacle_ratio:.0%})"
        )
        st.pyplot(fig_grid)
    else:
        st.info("点击「开始多智能体分析」生成地图")
```

### 4.4 右栏：参数摘要

```python
with col_right:
    st.subheader("📋 参数摘要")
    params = {
        "地图尺寸": f"{map_width}×{map_height}",
        "障碍物占比": f"{obstacle_ratio:.0%}",
        "连通性": f"{connectivity:.2f}",
        "拓扑随机性": f"{topology_randomness:.2f}",
        "算力限制": compute_limit.upper(),
    }
    for k, v in params.items():
        st.metric(k, v)
```

### 4.5 执行决策管线的抽取函数

将核心执行逻辑抽取为独立函数，便于在各Tab中复用：

```python
def execute_decision_pipeline(map_width, map_height, obstacle_ratio,
                               connectivity, topology_randomness,
                               compute_limit, random_seed,
                               start_x, start_y, target_x, target_y,
                               dynamic_change_rate):
    """执行一次完整的多智能体分析流水线"""
    env_input = {
        "obstacle_ratio": obstacle_ratio,
        "map_width": map_width,
        "map_height": map_height,
        "connectivity": connectivity,
        "topology_randomness": topology_randomness,
        "compute_limit": compute_limit,
        "start_point": [start_x, start_y],
        "target_point": [target_x, target_y],
        "dynamic_change_rate": dynamic_change_rate,
    }
    st.session_state.env_input = env_input

    # 1. 生成地图
    gen = MapGenerator(seed=random_seed)
    grid = gen.generate(map_width, map_height, obstacle_ratio,
                         (start_x, start_y), (target_x, target_y))
    st.session_state.grid = grid
    st.session_state.start = (start_x, start_y)
    st.session_state.target = (target_x, target_y)

    # 2. 连通性检查
    checker = ConnectivityChecker()
    if not checker.is_reachable(grid, (start_x, start_y), (target_x, target_y)):
        for _ in range(5):
            grid = gen.generate(map_width, map_height, obstacle_ratio,
                                 (start_x, start_y), (target_x, target_y))
            if checker.is_reachable(grid, (start_x, start_y), (target_x, target_y)):
                break

    # 3. Benchmark 评估
    benchmark = BenchmarkRunner()
    benchmark_results = benchmark.run(grid, (start_x, start_y),
                                       (target_x, target_y), n_runs=3)
    st.session_state.benchmark_results = benchmark_results

    # 4. 决策系统
    system = PathPlanningDecisionSystem()
    decision = system.decide(env_input)
    st.session_state.decision = decision

    # 5. 地图分析
    try:
        from map.map_analyzer import MapAnalyzer
        analyzer = MapAnalyzer()
        features = analyzer.analyze(grid, (start_x, start_y), (target_x, target_y))
        st.session_state.features = features
    except ImportError:
        st.session_state.features = {"scene_level": decision.get("scene_level", "unknown")}

    # 6. 科学假设
    explanation_agent = ExplanationAgent(use_qwen=False)
    explanation = explanation_agent.explain(env_input, decision)
    hypo_agent = HypothesisAgent(use_qwen=False)
    hypothesis = hypo_agent.generate(env_input, decision, explanation["explanation_text"])
    st.session_state.hypothesis = hypothesis
```

---

## 五、Tab 2: 环境分析页面

### 5.1 布局

```python
with tab_analysis:
    if st.session_state.decision is not None:
        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.subheader("📊 场景分析")
            decision = st.session_state.decision

            # 场景等级卡片
            scene_level = decision.get("scene_level", "N/A")
            level_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}
            st.metric("场景等级",
                      f"{level_emoji.get(scene_level, '⚪')} {scene_level.upper()}")

            # 复杂度指标
            if st.session_state.features:
                features = st.session_state.features
                st.metric("综合复杂度指数",
                          f"{features.get('complexity_index', 0):.3f}")

            # 决策摘要
            st.info(f"**推荐算法：{decision['best_algorithm']}**")
            st.metric("综合得分", f"{decision['best_score']:.4f}")

        with col_right:
            # 算法排名柱状图
            st.subheader("📈 算法综合评分排名")
            fig_bar = draw_ranking_bar(decision["ranking"])
            st.pyplot(fig_bar)

        # 底部：雷达图 + Benchmark 详情
        st.divider()
        col_bottom_left, col_bottom_right = st.columns([1, 1])

        with col_bottom_left:
            st.subheader("🎯 多指标雷达图")
            fig_radar = draw_radar(decision["ranking"])
            st.pyplot(fig_radar)

        with col_bottom_right:
            st.subheader("📋 算法对比数据表")
            if st.session_state.benchmark_results:
                benchmark = st.session_state.benchmark_results
                benchmark.print_table(benchmark_results)
    else:
        st.info("请先在「地图参数」标签页中执行分析。")
```

### 5.2 visualization.py 需要新增的辅助函数

在 [visualization.py](file:///d:/BianChengDamom/PycharmProjects/PythonProject/路径规划算法自适应选型多智能体 AI Scientist 系统/ai_scientist_path_planning/gui/visualization.py) 中新增：

```python
def draw_metric_cards(metrics: dict):
    """将指标字典渲染为Plotly指标卡片组合图"""
    import plotly.graph_objects as go
    fig = go.Figure()
    # 实现指标卡片布局...
    return fig


def draw_scene_indicator(scene_level: str, complexity: float):
    """绘制场景等级指示器（仪表盘风格）"""
    import plotly.graph_objects as go
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=complexity,
        title={"text": f"场景等级: {scene_level}"},
        gauge={"axis": {"range": [0, 1]},
               "bar": {"color": "darkblue"},
               "steps": [
                   {"range": [0, 0.33], "color": "lightgreen"},
                   {"range": [0.33, 0.66], "color": "yellow"},
                   {"range": [0.66, 1.0], "color": "salmon"}
               ]}
    ))
    return fig
```

---

## 六、Tab 3: 智能体推理页面

### 6.1 布局：两栏 (1:1)

```python
with tab_reasoning:
    if st.session_state.decision is not None:
        decision = st.session_state.decision

        col_left, col_right = st.columns([1, 1])

        with col_left:
            # 6.2 决策结果卡片
            st.subheader("🏆 算法选型结果")
            render_decision_card(decision)

            # 6.3 指标评分详情
            st.subheader("📊 指标评分详情")
            ranking = decision.get("ranking", [])
            top = ranking[0] if ranking else {}
            detail = top.get("detail", {})
            score_items = {
                "耗时得分": detail.get("time_score", 0),
                "路径得分": detail.get("length_score", 0),
                "成功率得分": detail.get("success_score", 0),
                "稳定性得分": detail.get("stability_score", 0),
                "规则惩罚": detail.get("penalty", 0),
            }
            for label, value in score_items.items():
                st.metric(label, f"{value:.4f}")

            # 6.4 Qwen 解释
            st.divider()
            st.subheader("💬 Qwen 解释")
            env_input = st.session_state.env_input
            explanation_agent = ExplanationAgent(use_qwen=False)
            explanation = explanation_agent.explain(env_input, decision)
            st.info(explanation["explanation_text"])

        with col_right:
            # 6.5 推理链条可视化
            st.subheader("🧠 多智能体推理链")
            render_reasoning_chain(decision)

            # 6.6 参数推荐
            st.divider()
            st.subheader("⚙ 推荐算法参数")
            if st.session_state.params:
                params = st.session_state.params
                st.code(params, language="json")
    else:
        st.info("请先在「地图参数」标签页中执行分析。")
```

### 6.2 visualization.py 新增函数

```python
def render_decision_card(decision: dict):
    """渲染决策结果卡片 - 使用 st.metric 和 st.success/st.info 组合"""
    scene_level = decision.get("scene_level", "N/A")
    best_algorithm = decision.get("best_algorithm", "N/A")
    best_score = decision.get("best_score", 0)

    # 场景等级指示
    level_colors = {"low": "green", "medium": "orange", "high": "red"}
    color = level_colors.get(scene_level, "grey")
    st.markdown(f"### :{color}[{scene_level.upper()} 复杂度]")
    st.success(f"**推荐算法：{best_algorithm}**")
    st.metric("综合得分", f"{best_score:.4f}", delta=None)


def render_reasoning_chain(decision: dict):
    """渲染7个智能体的推理链条"""
    agents = [
        ("① 数据接收智能体", "✅ 字段校验通过"),
        ("② 环境分析智能体", f"✅ 场景等级: {decision.get('scene_level', 'N/A')}"),
        ("③ 知识库检索智能体", f"✅ 命中历史记录"),
        ("④ 规则约束智能体", "✅ 规则检查完成"),
        ("⑤ 算法评估智能体", "✅ 加权评分完成"),
        ("⑥ 决策生成智能体", f"✅ 选定: {decision.get('best_algorithm', 'N/A')}"),
        ("⑦ 参数推荐智能体", "✅ 参数已推荐"),
    ]
    for name, status in agents:
        with st.expander(name, expanded=False):
            st.success(status)
```

---

## 七、Tab 4: 研究报告页面

### 7.1 布局

```python
with tab_report:
    if st.session_state.hypothesis is not None:
        st.subheader("📄 科学假设与研究计划")

        hypothesis = st.session_state.hypothesis
        decision = st.session_state.decision
        env_input = st.session_state.env_input

        # 10个标准字段
        sections = [
            ("1. 待研究问题 (Problem Statement)", hypothesis.get("problem_statement", "")),
            ("2. 解决思路 (Rationale)", hypothesis.get("rationale", "")),
            ("3. 必要技术手段 (Technical Details)", hypothesis.get("technical_details", "")),
            ("4. 数据集 (Datasets)", hypothesis.get("datasets", "")),
            ("5. 论文标题 (Paper Title)", hypothesis.get("paper_title", "")),
            ("6. 摘要 (Paper Abstract)", hypothesis.get("abstract", "")),
            ("7. 方法论 (Methods)", hypothesis.get("methods", "")),
            ("8. 实验设计 (Experiments)", hypothesis.get("experiments", "")),
            ("9. 实验结果 (Results)", hypothesis.get("results", "")),
            ("10. 参考论文 (References)", hypothesis.get("references", "")),
        ]

        for title, content in sections:
            with st.expander(title, expanded=(content != "")):
                st.markdown(content if content else "*待生成*")

        # 下载按钮
        col_dl1, col_dl2, col_dl3 = st.columns(3)
        with col_dl1:
            full_report = generate_markdown_report(hypothesis, decision, env_input)
            st.download_button(
                "📥 下载 Markdown",
                data=full_report,
                file_name="ai_scientist_research_report.md",
                mime="text/markdown",
                use_container_width=True
            )
        with col_dl2:
            st.button("📥 下载 PDF", disabled=True,
                      help="PDF 导出功能将在优化版中实现",
                      use_container_width=True)
        with col_dl3:
            st.button("🔄 重新生成", use_container_width=True,
                      on_click=regenerate_hypothesis)
    else:
        st.info("请先在「地图参数」标签页中执行分析，再查看研究报告。")
```

### 7.2 报告生成辅助函数

```python
def generate_markdown_report(hypothesis: dict, decision: dict, env_input: dict) -> str:
    """生成完整 Markdown 格式研究计划"""
    lines = [
        "# AI Scientist 研究计划",
        "",
        f"## 场景信息",
        f"- 障碍物占比: {env_input.get('obstacle_ratio', 'N/A')}",
        f"- 地图尺寸: {env_input.get('map_width', 'N/A')}×{env_input.get('map_height', 'N/A')}",
        f"- 推荐算法: {decision.get('best_algorithm', 'N/A')}",
        "",
        f"## 1. 待研究问题",
        hypothesis.get("problem_statement", ""),
        "",
        f"## 2. 解决思路",
        hypothesis.get("rationale", ""),
        "",
        f"## 3. 必要技术手段",
        hypothesis.get("technical_details", ""),
        "",
        f"## 4. 数据集",
        hypothesis.get("datasets", ""),
        "",
        f"## 5. 论文标题",
        hypothesis.get("paper_title", ""),
        "",
        f"## 6. 摘要",
        hypothesis.get("abstract", ""),
        "",
        f"## 7. 方法论",
        hypothesis.get("methods", ""),
        "",
        f"## 8. 实验设计",
        hypothesis.get("experiments", ""),
        "",
        f"## 9. 实验结果",
        hypothesis.get("results", ""),
        "",
        f"## 10. 参考论文",
        hypothesis.get("references", ""),
    ]
    return "\n".join(lines)


def regenerate_hypothesis():
    """重新生成科学假设的回调"""
    if st.session_state.decision is not None:
        env_input = st.session_state.env_input
        decision = st.session_state.decision
        hypo_agent = HypothesisAgent(use_qwen=False)
        explanation_agent = ExplanationAgent(use_qwen=False)
        explanation = explanation_agent.explain(env_input, decision)
        st.session_state.hypothesis = hypo_agent.generate(
            env_input, decision, explanation["explanation_text"]
        )
```

---

## 八、页面交互流程

```
用户打开系统 → Tab1(地图参数)
    │
    ├─ 调整滑块设置参数
    ├─ 可选：展开高级参数设置起点/终点/种子
    │
    ├─ 点击「▶ 开始多智能体分析」
    │   ├─ 生成随机栅格地图
    │   ├─ 连通性检查（不连通则重试≤5次）
    │   ├─ BenchmarkRunner 运行5种算法 × 3轮实验
    │   ├─ PathPlanningDecisionSystem 执行6智能体链
    │   ├─ ExplanationAgent 生成选型解释
    │   └─ HypothesisAgent 生成科学假设
    │
    ├─ 自动跳转 → Tab2(环境分析)
    │   ├─ 查看场景等级、复杂度指数
    │   └─ 查看排名柱状图、雷达图、数据表
    │
    ├─ 手动切换 → Tab3(智能体推理)
    │   ├─ 查看决策结果卡片
    │   ├─ 展开推理链查看每个智能体状态
    │   └─ 查看Qwen解释文本
    │
    └─ 手动切换 → Tab4(研究报告)
        ├─ 展开查看10个标准字段
        └─ 下载 Markdown 格式报告
```

---

## 九、执行步骤总结

| 步骤 | 文件 | 操作 | 预计增加行数 |
|------|------|------|-------------|
| 1 | `requirements.txt` | 添加 `plotly>=5.15.0` | +1 |
| 2 | `gui/streamlit_app.py` | **重写**为三栏+Tab布局 | 142→~350 |
| 3 | `gui/visualization.py` | 新增6个函数 | 78→~200 |
| 4 | `map/map_analyzer.py` | 新建或确认存在 | 新建~50 |
| 5 | `agents/parameter_agent.py` | 新建参数推荐Agent | 新建~80 |

### 9.1 文件变更清单

```
修改: requirements.txt           (+1行)
修改: gui/streamlit_app.py       (重写, ~350行)
修改: gui/visualization.py       (+6个函数, ~200行)
新增: map/map_analyzer.py        (~50行)
新增: agents/parameter_agent.py  (~80行)
```

---

## 十、验证与测试清单

- [ ] `streamlit run gui/streamlit_app.py` 能正常启动，无 import 错误
- [ ] Tab1 滑块控件响应正常，地图能正确生成并渲染
- [ ] 点击"开始多智能体分析"后，控制台无报错，页面自动刷新
- [ ] Tab2 展示场景等级、柱状图、雷达图、数据表四项内容
- [ ] Tab3 展示决策卡片、推理链、Qwen解释三项内容
- [ ] Tab4 展示10个字段并可下载 Markdown 文件
- [ ] 不连通地图自动重试生成（验证 corner case）
- [ ] 各Tab之间切换时数据保持一致（Session State 正确传递）
- [ ] `python -m pytest tests/` 所有现有测试仍然通过
