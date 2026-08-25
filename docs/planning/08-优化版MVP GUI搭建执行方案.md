# 优化版 MVP GUI 搭建执行方案

> 基于 [基础版与优化版MVP GUI界面设计方案.md](基础版与优化版MVP%20GUI界面设计方案.md) 中提取的所有优化方向，扩展为分阶段可执行的升级方案。
> 前置条件：基础版 [07-基础版MVP GUI搭建执行方案.md](07-基础版MVP%20GUI搭建执行方案.md) 已执行完成，GUI 可正常运行。

---

## 一、概述

### 1.1 目标

在基础版 GUI 之上，分 **3个阶段** 渐进式升级，最终达到具备学术展示级品质的交互式 AI Scientist 界面。

### 1.2 优化策略

```
风险等级：  Phase 1 (低)  →  Phase 2 (中)  →  Phase 3 (高)
变更规模：  小步快跑        功能扩展         架构级改动
适用场景：  赛前快速打磨     赛中展示优化     赛后深度迭代
```

### 1.3 前置条件

- [x] 07 基础版 GUI 已完成并正常运行
- [x] 所有基础版测试通过
- [ ] Plotly 已安装（基础版已引入）
- [ ] 如需 3D 渲染，安装额外依赖

### 1.4 技术栈扩展

| 组件 | 选型 | 用途 | 所属阶段 |
|------|------|------|---------|
| Plotly | 交互式图表 + 3D | 替代 Matplotlib 静态图 | Phase 1 |
| streamlit-autorefresh | 定时刷新 | 动画帧驱动 | Phase 1 |
| Plotly animate | 动画帧 | 搜索过程动画 | Phase 1 |
| streamlit-drawable-canvas | 画布组件 | 交互式地图编辑 | Phase 2 |
| streamlit-aggrid | 高级表格 | 可排序/筛选数据表 | Phase 2 |
| pdfkit / WeasyPrint | HTML→PDF | PDF 报告导出 | Phase 2 |
| streamlit-components | 自定义前端 | Three.js 3D 渲染 | Phase 3 |
| Docker | 容器化 | 生产环境部署 | Phase 3 |
| scikit-learn | 机器学习 | 性能预测模型 | Phase 3 |

---

## 二、Phase 1: 视觉与交互增强

**风险等级：低** | **预计改动：~200行** | **依赖：Plotly**

### 2.1 路径搜索动画

**目标**：在地图上动态展示 A*/ACO/PSO 等算法的搜索过程，而非仅显示最终路径。

**实现方案**：

```python
# gui/animation.py — 新建文件

import plotly.graph_objects as go
import numpy as np

def create_search_animation(grid, algorithm, start, target):
    """
    生成搜索过程动画。
    - A*: 逐步显示 open/closed set 扩展
    - ACO: 逐步显示信息素分布 + 蚂蚁路径
    - PSO: 逐步显示粒子群移动
    """
    frames = []
    # 根据算法类型生成动画帧
    if algorithm == "astar":
        frames = _astar_step_frames(grid, start, target)
    elif algorithm == "aco":
        frames = _aco_step_frames(grid, start, target)
    elif algorithm == "pso":
        frames = _pso_step_frames(grid, start, target)

    fig = go.Figure(
        data=frames[0],
        layout=go.Layout(
            updatemenus=[{
                "type": "buttons",
                "buttons": [{
                    "label": "▶ 播放搜索过程",
                    "method": "animate",
                    "args": [None]
                }]
            }]
        ),
        frames=[go.Frame(data=f) for f in frames[1:]]
    )
    return fig
```

**修改文件**：
- 新建 [`gui/animation.py`](file:///d:/BianChengDamom/PycharmProjects/PythonProject/路径规划算法自适应选型多智能体 AI Scientist 系统/ai_scientist_path_planning/gui/animation.py)
- 修改 `gui/streamlit_app.py`：在中栏地图区添加动画播放按钮

### 2.2 多路径同屏对比

**目标**：在地图上叠加显示5种算法的最终路径，不同颜色区分。

```python
# gui/visualization.py 新增函数

def draw_multi_path_overlay(grid, paths: dict, start, target):
    """
    同屏显示多算法路径。
    paths: {"A*": [(x,y),...], "ACO": [...], ...}
    """
    import plotly.graph_objects as go

    colors = {
        "A*": "#e74c3c",
        "ACO": "#3498db",
        "PSO": "#2ecc71",
        "SA": "#f39c12",
        "Hybrid": "#9b59b6",
    }
    fig = go.Figure()
    # 绘制障碍物背景
    # 逐算法绘制路径
    for algo, path in paths.items():
        if path:
            xs = [p[0] for p in path]
            ys = [p[1] for p in path]
            fig.add_trace(go.Scatter(
                x=xs, y=ys, mode="lines",
                name=algo, line=dict(color=colors.get(algo, "#000"), width=2)
            ))
    fig.update_layout(title="多算法路径对比")
    return fig
```

**修改文件**：
- `gui/visualization.py` — 新增 `draw_multi_path_overlay` 函数
- `gui/streamlit_app.py` — Tab2 中栏增加"显示所有算法路径"按钮

### 2.3 指标切换动画

**目标**：柱状图点击切换指标时有平滑过渡。

```python
# 在 benchmark_results 中存储多指标数据
# 使用 Plotly dropdown 菜单切换指标维度

def draw_animated_bar_chart(ranking: list, metrics: list):
    """带下拉菜单切换的多指标柱状图"""
    import plotly.graph_objects as go

    fig = go.Figure()
    for metric in metrics:
        values = [r["detail"].get(f"{metric}_score", 0) for r in ranking]
        fig.add_trace(go.Bar(
            x=[r["algorithm"] for r in ranking],
            y=values,
            name=metric,
            visible=(metric == metrics[0])
        ))

    # 下拉切换菜单
    buttons = []
    for i, metric in enumerate(metrics):
        visibility = [j == i for j in range(len(metrics))]
        buttons.append(dict(label=metric, method="update",
                           args=[{"visible": visibility}]))
    fig.update_layout(
        updatemenus=[dict(active=0, buttons=buttons, x=1.15, y=1.2)]
    )
    return fig
```

**修改文件**：
- `gui/visualization.py` — 新增 `draw_animated_bar_chart` 函数
- `gui/streamlit_app.py` — Tab2 用新函数替换静态柱状图

### 2.4 可交互图表（悬停提示 + 图例切换）

**目标**：所有图表从 Matplotlib 升级为 Plotly，支持悬停查看数值、点击图例切换显示。

**修改策略**：
- `draw_ranking_bar` → 用 Plotly 重写，添加 `hover_data`
- `draw_radar` → 用 Plotly 重写，添加 `hovertemplate`
- `draw_grid` → 用 Plotly `go.Heatmap` 重写，更清晰的渲染

**修改文件**：
- `gui/visualization.py` — 所有 Matplotlib 函数重写为 Plotly 版本（约150行）
- `gui/streamlit_app.py` — `st.pyplot()` 全部替换为 `st.plotly_chart()`

### 2.5 验证清单 (Phase 1)

- [ ] A* 搜索动画可播放，帧率流畅（≥10fps）
- [ ] 多路径叠加图5种算法不同颜色清晰可辨
- [ ] 柱状图下拉切换指标有平滑过渡
- [ ] 所有图表支持悬停提示
- [ ] Matplotlib 依赖可移除（无 `st.pyplot` 调用）

---

## 三、Phase 2: 功能扩展

**风险等级：中** | **预计改动：~500行** | **依赖：streamlit-drawable-canvas, pdfkit**

### 3.1 10指标雷达图扩展

**目标**：从当前4维（耗时/路径/成功率/稳定性）扩展到10维。

**新增6个指标**：

| 指标 | 含义 | 数据来源 |
|------|------|---------|
| 安全性 | 路径是否远离障碍物 | 计算路径点与障碍物最小距离 |
| 平滑度 | 路径弯曲程度 | 计算路径转角总和 |
| 搜索效率 | 搜索节点数 / 地图面积 | BenchmarkRunner 记录 |
| 内存消耗 | 算法运行时内存占用 | 用 `tracemalloc` 测量 |
| 鲁棒性 | 多次运行结果的标准差 | 多轮实验统计 |
| 可扩展性 | 大尺寸地图下性能衰减率 | 多尺寸基准测试 |

```python
# gui/visualization.py 新增

def draw_extended_radar(ranking: list, metrics_10: list):
    """
    10维雷达图。需先扩展 BenchmarkRunner 收集额外指标。
    """
    import plotly.graph_objects as go
    N = len(metrics_10)
    angles = [n / N * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    fig = go.Figure()
    for r in ranking[:5]:
        detail = r.get("detail", {})
        values = [detail.get(m, 0) for m in metrics_10]
        values += values[:1]
        fig.add_trace(go.Scatterpolar(
            r=values, theta=metrics_10,
            name=r["algorithm"], fill="toself"
        ))
    return fig
```

**修改文件**：
- `evaluation/benchmark.py` — 扩展 BenchmarkRunner 收集额外6项指标
- `gui/visualization.py` — 新增 `draw_extended_radar`
- `gui/streamlit_app.py` — Tab2 增加"10指标雷达图"视图切换

### 3.2 误差线与置信区间

**目标**：在柱状图和雷达图上显示多次实验的标准差。

**实现**：在 BenchmarkRunner 中增加 `n_runs ≥ 5` 时计算均值和标准差，图表用 `error_y` 参数显示。

```python
# 在 draw_ranking_bar 的 Plotly 版本中
fig.add_trace(go.Bar(
    x=names, y=means,
    error_y=dict(type="data", array=stds, visible=True),
    name="综合得分"
))
```

**修改文件**：
- `evaluation/benchmark.py` — BenchmarkResult 增加 std 字段
- `gui/visualization.py` — 图表增加 error_y 参数

### 3.3 Pareto 前沿高亮

**目标**：在多目标空间中高亮标记非支配解集。

```python
def highlight_pareto_front(ranking: list):
    """
    在散点图/雷达图中高亮 Pareto 最优算法。
    Pareto 最优 = 不存在另一个算法在所有指标上都优于它。
    """
    # 使用 耗时 vs 路径长度 的二维散点图
    # 标记所有非支配点
    pass
```

### 3.4 分面/分组柱状图

**目标**：支持多组地图参数下同一算法的性能对比。

```python
# 在 streamlit_app.py 中添加
with st.expander("📊 批量对比模式"):
    uploaded_file = st.file_uploader("上传参数 CSV", type=["csv"])
    if uploaded_file:
        results = run_batch_benchmark(uploaded_file)
        fig = draw_faceted_comparison(results)  # 按复杂度分面
        st.plotly_chart(fig)
```

### 3.5 交互式地图编辑

**目标**：用户可以用鼠标在地图上点击添加/删除障碍物，拖拽改变起点终点。

```python
# 使用 streamlit-drawable-canvas
from streamlit_drawable_canvas import st_canvas

canvas_result = st_canvas(
    fill_color="rgba(0, 0, 0, 0.3)",
    stroke_width=0,
    background_image=grid_image,
    width=500, height=500,
    drawing_mode="point",
    key="map_editor",
)
```

**依赖新增**：`pip install streamlit-drawable-canvas`

### 3.6 地图预设模板库

**目标**：内置一键切换的地图模板。

```python
MAP_TEMPLATES = {
    "迷宫型": {"obstacle_ratio": 0.45, "connectivity": 0.30, "topology_randomness": 0.20},
    "空旷型": {"obstacle_ratio": 0.10, "connectivity": 0.90, "topology_randomness": 0.50},
    "窄通道型": {"obstacle_ratio": 0.55, "connectivity": 0.25, "topology_randomness": 0.30},
    "岛链型": {"obstacle_ratio": 0.35, "connectivity": 0.40, "topology_randomness": 0.80},
    "密集障碍": {"obstacle_ratio": 0.75, "connectivity": 0.15, "topology_randomness": 0.60},
}

# 在 streamlit_app.py Tab1 左栏添加
template = st.selectbox("快速模板", list(MAP_TEMPLATES.keys()))
if template:
    preset = MAP_TEMPLATES[template]
    # 自动填充参数滑块
```

### 3.7 动态障碍物模拟

**目标**：支持障碍物随时间变化的动态场景。

```python
# map/map_generator.py 新增
class DynamicMapGenerator:
    def __init__(self, seed):
        self.seed = seed

    def step(self, grid, change_rate=0.05):
        """随机翻转 change_rate 比例的格子，模拟障碍物移动"""
        pass
```

```python
# gui/streamlit_app.py 中
if dynamic_change_rate > 0:
    st.write("🔄 动态障碍物模式")
    frame_count = st.slider("模拟步数", 1, 100, 10)
    for t in range(frame_count):
        grid = dynamic_gen.step(grid, dynamic_change_rate)
        # 重新规划路径
```

### 3.8 地图文件上传

**目标**：支持上传 CSV/JSON 格式的真实栅格地图。

```python
uploaded_file = st.file_uploader("上传地图文件", type=["csv", "json"])
if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        grid = np.loadtxt(uploaded_file, delimiter=",")
    elif uploaded_file.name.endswith(".json"):
        grid = np.array(json.load(uploaded_file)["grid"])
    st.session_state.uploaded_grid = grid
```

### 3.9 批量参数输入与对比

**目标**：CSV 批量导入多组地图参数，自动运行并生成对比报告。

```python
# 支持 CSV 格式：
# obstacle_ratio,map_width,map_height,connectivity,compute_limit
# 0.10,100,100,0.90,high
# 0.35,200,200,0.68,medium
# 0.60,300,300,0.35,low

def run_batch_mode(csv_data):
    """批量运行多组参数，返回对比结果"""
    results = []
    for row in csv_data:
        decision = system.decide(row)
        results.append(decision)
    return results
```

### 3.10 推理链交互增强

**目标**：每个智能体卡片可展开查看完整输入/输出 JSON，添加置信度进度条。

```python
def render_enhanced_reasoning_chain(decision: dict):
    """增强版推理链条"""
    chain_steps = [
        {
            "name": "① 数据接收智能体",
            "confidence": 1.0,
            "input": {"fields_received": 6},
            "output": {"validation": "passed", "errors": []}
        },
        {
            "name": "② 环境分析智能体",
            "confidence": 0.95,
            "input": env_input,
            "output": {"scene_level": decision["scene_level"]}
        },
        # ... 其他智能体
    ]
    for step in chain_steps:
        with st.expander(f"{step['name']} 置信度: {step['confidence']:.0%}", expanded=False):
            st.progress(step["confidence"])
            col_in, col_out = st.columns(2)
            with col_in:
                st.json(step["input"])
            with col_out:
                st.json(step["output"])
```

### 3.11 PDF 导出

**目标**：支持将研究报告导出为 PDF。

```python
# requirements.txt 新增
# pdfkit==1.0.0

import pdfkit

def export_pdf(markdown_content: str, output_path: str):
    """将 Markdown 报告转为 PDF"""
    html = markdown.markdown(markdown_content)
    pdfkit.from_string(html, output_path)
```

### 3.12 验证清单 (Phase 2)

- [ ] 10指标雷达图可正常渲染，数据来源准确
- [ ] 误差线在图表中正确显示
- [ ] Pareto 前沿标记与非支配解集一致
- [ ] 批量模式可处理 ≥10 组参数
- [ ] 画布地图编辑无延迟
- [ ] 模板切换时参数滑块同步更新
- [ ] 动态障碍物每帧地图正确更新
- [ ] 文件上传 CSV/JSON 正常解析
- [ ] 推理链展开后 JSON 格式正确
- [ ] PDF 导出文件可正常打开

---

## 四、Phase 3: 高级特性

**风险等级：高** | **预计改动：~800行** | **依赖：Three.js, Docker, scikit-learn**

### 4.1 3D 体素地图渲染

**目标**：用 Three.js 渲染三维体素地图，支持旋转、缩放。

**实现方案**：通过 `streamlit-components` 嵌入自定义 HTML/JS：

```python
# gui/threejs_renderer.py

def render_3d_voxel_map(grid_3d: np.ndarray):
    """使用 Three.js 渲染3D体素地图"""
    html = f"""
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <div id="voxel-container" style="width:600px;height:600px"></div>
    <script>
        // Three.js 场景初始化
        // 根据 grid_3d 数据创建体素
    </script>
    """
    return st.components.v1.html(html, height=650)
```

**依赖**：无需额外 Python 包（纯前端 JS），但需要 `streamlit>=1.28` 的 `components` 支持。

### 4.2 多智能体辩论可视化

**目标**：两个持不同观点的智能体以对话气泡形式辩论。

```python
def render_agent_debate(agent_a: str, agent_b: str, topic: str, rounds: list):
    """
    可视化多智能体辩论过程。
    rounds: [{"speaker": "A", "content": "...", "confidence": 0.8}, ...]
    """
    for i, r in enumerate(rounds):
        if r["speaker"] == "A":
            st.chat_message("assistant", avatar="🧠").write(
                f"**{agent_a}** (置信度: {r['confidence']:.0%})\n\n{r['content']}"
            )
        else:
            st.chat_message("user", avatar="🤖").write(
                f"**{agent_b}** (置信度: {r['confidence']:.0%})\n\n{r['content']}"
            )
```

### 4.3 多轮人在回路对话交互

**目标**：用户能与系统进行多轮对话，询问"为什么排除 A*？"等。

```python
# 在 Tab3 中添加对话区
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_query = st.chat_input("向 AI Scientist 提问...")
if user_query:
    response = human_loop_agent.respond(user_query, st.session_state.decision)
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    st.session_state.chat_history.append({"role": "assistant", "content": response})

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
```

### 4.4 敏感度分析报告

**目标**：展示各指标权重微小变化对最终选型结果的影响。

```python
def sensitivity_analysis(decision_system, env_input, delta=0.05):
    """
    对每个指标权重 ±delta，观察推荐算法是否变化。
    返回敏感度矩阵。
    """
    weights = ["time", "length", "success", "stability"]
    results = {}
    for w in weights:
        for direction in [-1, 1]:
            modified = env_input.copy()
            modified[f"{w}_weight"] += direction * delta
            new_decision = decision_system.decide(modified)
            changed = new_decision["best_algorithm"] != original["best_algorithm"]
            results[f"{w}_{'+' if direction>0 else '-'}{delta}"] = {
                "algorithm": new_decision["best_algorithm"],
                "changed": changed,
            }
    return results
```

### 4.5 权重动态调整与实时重算

**目标**：在雷达图上直接拖拽调整指标权重，实时更新所有图表。

**实现思路**：
```python
# 使用 Streamlit slider 配合 callback 实现近似实时更新
col_w1, col_w2, col_w3, col_w4 = st.columns(4)
with col_w1:
    w_time = st.slider("耗时权重", 0.0, 1.0, 0.25, 0.05, key="w_time",
                        on_change=recalculate)
with col_w2:
    w_length = st.slider("路径权重", 0.0, 1.0, 0.30, 0.05, key="w_length",
                          on_change=recalculate)
# ...

def recalculate():
    """权重变更时重新计算排名"""
    env_input = st.session_state.env_input
    env_input["custom_weights"] = {
        "time": st.session_state.w_time,
        "length": st.session_state.w_length,
        "success": st.session_state.w_success,
        "stability": st.session_state.w_stability,
    }
    system = PathPlanningDecisionSystem()
    new_decision = system.decide(env_input)
    st.session_state.decision = new_decision
```

### 4.6 LaTeX 论文导出

**目标**：自动生成 LaTeX 格式的论文源码。

```python
def generate_latex_paper(hypothesis: dict, decision: dict, figures: list):
    """生成 LaTeX 论文源码"""
    template = r"""
\documentclass{{article}}
\title{{{title}}}
\begin{{document}}
\maketitle
\begin{{abstract}}
{abstract}
\end{{abstract}}
\section{{Introduction}}
{problem_statement}
\section{{Methods}}
{methods}
\section{{Experiments}}
{experiments}
\section{{Results}}
{results}
\bibliographystyle{{plain}}
\bibliography{{references}}
\end{{document}}
""".format(
        title=hypothesis.get("paper_title", ""),
        abstract=hypothesis.get("abstract", ""),
        problem_statement=hypothesis.get("problem_statement", ""),
        methods=hypothesis.get("methods", ""),
        experiments=hypothesis.get("experiments", ""),
        results=hypothesis.get("results", ""),
    )
    return template
```

### 4.7 文献自动检索集成

**目标**：接入论文数据库 API，自动检索相关论文并生成参考文献。

```python
def search_papers(topic: str, max_results: int = 10):
    """
    使用 Semantic Scholar API 检索相关论文。
    API: https://api.semanticscholar.org/graph/v1/paper/search
    """
    import requests
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {"query": topic, "limit": max_results, "fields": "title,authors,year"}
    resp = requests.get(url, params=params)
    return resp.json().get("data", [])
```

### 4.8 审稿人模拟

**目标**：内置 AI 审稿人智能体，自动评审生成的假设和创新性。

```python
# agents/reviewer_agent.py — 新建

class ReviewerAgent:
    """AI 审稿人智能体"""

    def review(self, hypothesis: dict) -> dict:
        """评审科学假设，返回评分和意见"""
        return {
            "novelty_score": 0.0,       # 创新性评分
            "feasibility_score": 0.0,    # 可行性评分
            "rigor_score": 0.0,          # 严谨性评分
            "overall_score": 0.0,        # 综合评分
            "strengths": [],             # 优点列表
            "weaknesses": [],            # 缺点列表
            "suggestions": [],           # 改进建议
        }
```

### 4.9 Docker 容器化部署

**目标**：将 Streamlit 应用打包为 Docker 镜像。

```dockerfile
# Dockerfile — 项目根目录新建

FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "ai_scientist_path_planning/gui/streamlit_app.py", \
     "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
# 构建与运行
docker build -t ai-scientist-gui .
docker run -p 8501:8501 ai-scientist-gui
```

### 4.10 性能预测模型集成

**目标**：用机器学习模型替代查表式评分，预测算法在未知场景下的性能。

```python
# evaluation/predictor.py — 新建

from sklearn.ensemble import RandomForestRegressor
import numpy as np

class PerformancePredictor:
    """基于历史数据的算法性能预测器"""

    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100)

    def train(self, historical_data: list):
        """
        训练数据格式: [(features, performance_vector), ...]
        features: [obstacle_ratio, map_size, connectivity, ...]
        performance_vector: [time, length, success_rate, stability]
        """
        X = np.array([d[0] for d in historical_data])
        y = np.array([d[1] for d in historical_data])
        self.model.fit(X, y)

    def predict(self, features: list) -> dict:
        """预测5种算法的性能"""
        pred = self.model.predict([features])
        return {
            "time": pred[0][0],
            "length": pred[0][1],
            "success_rate": pred[0][2],
            "stability": pred[0][3],
        }
```

### 4.11 实验闭环自动迭代

**目标**：系统自动生成假设 → 运行实验 → 分析结果 → 更新知识库 → 修正假设的闭环。

```python
def auto_experiment_loop(env_input, max_iterations=10):
    """自动迭代实验闭环"""
    results_log = []
    for i in range(max_iterations):
        # 1. 执行决策
        decision = system.decide(env_input)
        # 2. 记录结果
        results_log.append(decision)
        # 3. 更新知识库
        knowledge_agent.update(decision)
        # 4. 生成新的科学假设
        hypothesis = hypothesis_agent.generate(env_input, decision)
        # 5. 收敛检查
        if i > 1 and results_log[-1]["best_algorithm"] == results_log[-2]["best_algorithm"]:
            break
    return results_log
```

### 4.12 多机器人协同路径可视化

**目标**：支持多起点多终点的多机器人路径规划与冲突检测可视化。

```python
def draw_multi_robot_paths(grid, robot_tasks: list):
    """
    多机器人路径可视化。
    robot_tasks: [
        {"id": "R1", "start": (0,0), "target": (50,50), "path": [...]},
        {"id": "R2", "start": (100,0), "target": (50,100), "path": [...]},
    ]
    """
    import plotly.graph_objects as go
    fig = go.Figure()
    # 绘制障碍物背景
    # 逐机器人绘制路径（不同颜色）
    colors = px.colors.qualitative.Plotly
    for i, robot in enumerate(robot_tasks):
        xs = [p[0] for p in robot["path"]]
        ys = [p[1] for p in robot["path"]]
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="lines+markers",
            name=robot["id"],
            line=dict(color=colors[i % len(colors)], width=2)
        ))
    return fig
```

### 4.13 验证清单 (Phase 3)

- [ ] 3D 地图可旋转缩放，渲染性能 ≥30fps
- [ ] 辩论视图两个智能体交替发言
- [ ] 对话输入可连续多轮交互
- [ ] 敏感度矩阵正确反映权重变化影响
- [ ] 权重拖动后图表实时更新，延迟 <500ms
- [ ] LaTeX 生成的 .tex 文件可编译为 PDF
- [ ] 文献检索返回论文标题和作者
- [ ] 审稿人评分在合理范围内（0-1）
- [ ] Docker 构建成功，容器启动后可访问
- [ ] 预测模型预测值与实际值的 MAE <0.1
- [ ] 实验循环自动收敛至稳定状态

---

## 五、技术选型建议

| 需求 | 推荐方案 | 备选方案 | 选型理由 |
|------|---------|---------|---------|
| 3D 渲染 | Plotly 3D (go.Scatter3d) | Three.js | Plotly 无需 JS 开发，Streamlit 原生支持 |
| 动画 | Plotly animate | streamlit-autorefresh | Plotly animate 更流畅，无需全页刷新 |
| 交互编辑 | streamlit-drawable-canvas | Custom component | 社区维护，纯 Python 接口 |
| PDF 导出 | pdfkit (wkhtmltopdf) | WeasyPrint / ReportLab | 对中文支持好，Markdown→HTML→PDF |
| 高级表格 | streamlit-aggrid | st.dataframe | 支持排序、筛选、导出 |
| ML 预测 | RandomForestRegressor | XGBoost | sklearn 零额外依赖，可解释性好 |
| 文献检索 | Semantic Scholar API | arXiv API | 免费、无需 API Key、结构化数据 |
| 容器化 | Docker | 阿里云 ECS 直接部署 | 环境一致性、可移植性好 |

---

## 六、执行优先级排序

按 **价值/成本** 矩阵排序优先级：

| 优先级 | 优化项 | 价值 | 成本 | 阶段 |
|--------|--------|------|------|------|
| P0 | 图表 Plotly 化（交互+悬停） | 高 | 低 | Phase 1 |
| P0 | 多路径同屏对比 | 高 | 低 | Phase 1 |
| P1 | 搜索动画 | 高 | 中 | Phase 1 |
| P1 | 10指标雷达图 | 中 | 中 | Phase 2 |
| P1 | 推理链交互增强 | 中 | 中 | Phase 2 |
| P1 | PDF 导出 | 高 | 低 | Phase 2 |
| P2 | 地图预设模板 | 中 | 低 | Phase 2 |
| P2 | 文件上传 | 中 | 低 | Phase 2 |
| P2 | 误差线与置信区间 | 中 | 中 | Phase 2 |
| P2 | 批量参数对比 | 中 | 中 | Phase 2 |
| P3 | 交互式地图编辑 | 中 | 高 | Phase 2 |
| P3 | 动态障碍物模拟 | 低 | 高 | Phase 2 |
| P4 | 3D 体素渲染 | 高 | 高 | Phase 3 |
| P4 | 多轮对话交互 | 高 | 高 | Phase 3 |
| P4 | 敏感度分析 | 高 | 高 | Phase 3 |
| P4 | LaTeX 导出 | 高 | 高 | Phase 3 |
| P5 | 多智能体辩论 | 中 | 高 | Phase 3 |
| P5 | 审稿人模拟 | 中 | 高 | Phase 3 |
| P5 | 性能预测模型 | 中 | 高 | Phase 3 |
| P6 | 文献自动检索 | 低 | 中 | Phase 3 |
| P6 | Docker 部署 | 低 | 中 | Phase 3 |
| P6 | 实验闭环 | 低 | 高 | Phase 3 |
| P6 | 多机器人路径 | 低 | 高 | Phase 3 |

---

## 七、文件变更汇总

| 阶段 | 文件 | 操作 | 预计行数 |
|------|------|------|---------|
| Phase 1 | `gui/visualization.py` | Matplotlib→Plotly 重写 | 78→~250 |
| Phase 1 | `gui/animation.py` | 新建搜索动画模块 | ~120 |
| Phase 1 | `gui/streamlit_app.py` | 替换图表调用方式 | +30 |
| Phase 2 | `gui/visualization.py` | 新增10指标/Pareto等函数 | +100 |
| Phase 2 | `evaluation/benchmark.py` | 扩展指标收集 | +50 |
| Phase 2 | `gui/streamlit_app.py` | 新增批量/文件上传/模板 | +150 |
| Phase 2 | `map/map_generator.py` | 新增 DynamicMapGenerator | ~80 |
| Phase 2 | `requirements.txt` | 新增依赖 | +3 |
| Phase 3 | `gui/threejs_renderer.py` | 新建3D渲染模块 | ~100 |
| Phase 3 | `agents/reviewer_agent.py` | 新建审稿人Agent | ~80 |
| Phase 3 | `evaluation/predictor.py` | 新建性能预测器 | ~100 |
| Phase 3 | `Dockerfile` | 新建容器配置文件 | ~15 |
| Phase 3 | `requirements.txt` | 新增依赖 | +5 |

---

## 八、风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| Plotly 大图渲染性能 | 页面卡顿 | 限制地图尺寸 ≤200×200，图景点数 ≤5000 |
| Three.js 浏览器兼容 | 部分浏览器不显示 | 提供 Plotly 3D 备选方案 |
| PDF 中文乱码 | 报告不可读 | 使用 wkhtmltopdf 并配置中文字体 |
| 文献 API 限流 | 检索失败 | 实现本地缓存，失败时使用静态列表 |
| Docker 构建过大 | 部署时间过长 | 使用 slim 基础镜像，多阶段构建 |
