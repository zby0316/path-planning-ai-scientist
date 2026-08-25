from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle


OUT = Path(__file__).resolve().parents[2] / "assets" / "reports" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

COLORS = {
    "blue": "#2F6B9A",
    "cyan": "#2A9D8F",
    "green": "#5A9F68",
    "orange": "#E9A23B",
    "red": "#D95D5D",
    "purple": "#8064A2",
    "light": "#F4F7FA",
    "dark": "#243746",
    "gray": "#697A89",
}


def canvas(figsize=(12, 7), title=""):
    fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    if title:
        ax.text(0.5, 0.965, title, ha="center", va="top", fontsize=18, fontweight="bold", color=COLORS["dark"])
    return fig, ax


def box(ax, xy, wh, text, fc="#FFFFFF", ec=None, fontsize=11, weight="normal", radius=0.025, text_color=None):
    x, y = xy
    w, h = wh
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.012,rounding_size={radius}",
        linewidth=1.5,
        edgecolor=ec or COLORS["gray"],
        facecolor=fc,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize, fontweight=weight, color=text_color or COLORS["dark"], wrap=True)
    return patch


def arrow(ax, start, end, color=None, style="-|>", width=1.5, connectionstyle="arc3"):
    patch = FancyArrowPatch(start, end, arrowstyle=style, mutation_scale=13, linewidth=width, color=color or COLORS["gray"], connectionstyle=connectionstyle)
    ax.add_patch(patch)
    return patch


def save(fig, name):
    fig.savefig(OUT / name, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig_1_1():
    fig, ax = canvas(title="路径规划算法自适应选型问题")
    inputs = [
        ("障碍率", "#DCEAF5"), ("连通性", "#DCEAF5"), ("拓扑随机性", "#DCEAF5"),
        ("动态变化率", "#DCEAF5"), ("算力限制", "#DCEAF5"), ("优化偏好", "#DCEAF5"),
    ]
    for i, (label, color) in enumerate(inputs):
        row, col = divmod(i, 3)
        box(ax, (0.04 + col * 0.14, 0.66 - row * 0.18), (0.11, 0.10), label, fc=color, ec=COLORS["blue"])
        arrow(ax, (0.15 + col * 0.14, 0.71 - row * 0.18), (0.47, 0.55), COLORS["blue"])
    box(ax, (0.44, 0.43), (0.20, 0.23), "环境特征分析\n+\n规则约束\n多指标评分", fc="#E7F3EF", ec=COLORS["cyan"], fontsize=13, weight="bold")
    algos = ["A*", "ACO", "PSO", "SA", "混合优化"]
    for i, label in enumerate(algos):
        box(ax, (0.73, 0.73 - i * 0.13), (0.11, 0.08), label, fc="#FCECCF", ec=COLORS["orange"], weight="bold")
        arrow(ax, (0.64, 0.55), (0.73, 0.77 - i * 0.13), COLORS["orange"])
    box(ax, (0.86, 0.40), (0.11, 0.20), "推荐算法\n参数配置\n解释与置信度", fc="#E7DFF1", ec=COLORS["purple"], fontsize=12, weight="bold")
    for i in range(5):
        arrow(ax, (0.84, 0.77 - i * 0.13), (0.89, 0.60), COLORS["purple"])
    box(ax, (0.38, 0.10), (0.28, 0.13), "实验反馈 → 反思修订 → 知识回流", fc="#F8E2E2", ec=COLORS["red"], fontsize=13, weight="bold")
    arrow(ax, (0.91, 0.40), (0.66, 0.18), COLORS["red"], connectionstyle="arc3,rad=-0.15")
    arrow(ax, (0.38, 0.18), (0.54, 0.43), COLORS["red"], connectionstyle="arc3,rad=-0.18")
    save(fig, "图1-1_路径规划算法自适应选型问题示意图.png")


def fig_1_2():
    fig, ax = canvas(figsize=(13, 6), title="路径规划与 AI Scientist 技术演进")
    ax.plot([0.07, 0.94], [0.48, 0.48], color=COLORS["gray"], linewidth=3)
    events = [
        (1959, "Dijkstra\n最短路", COLORS["blue"], 0.08),
        (1968, "A*\n启发式搜索", COLORS["blue"], 0.19),
        (1983, "模拟退火", COLORS["orange"], 0.30),
        (1995, "D* / PSO", COLORS["orange"], 0.41),
        (1996, "ACO / PRM", COLORS["orange"], 0.52),
        (2002, "D* Lite", COLORS["cyan"], 0.63),
        (2019, "自动算法选择", COLORS["green"], 0.74),
        (2020, "RAG", COLORS["purple"], 0.82),
        (2023, "LLM Agent\nReAct / Reflexion", COLORS["purple"], 0.89),
        (2024, "AI Scientist", COLORS["red"], 0.96),
    ]
    for i, (year, label, color, x) in enumerate(events):
        above = i % 2 == 0
        y2 = 0.68 if above else 0.28
        ax.scatter([x], [0.48], s=90, color=color, zorder=4)
        ax.plot([x, x], [0.48, y2], color=color, linewidth=1.5)
        ax.text(x, y2 + (0.03 if above else -0.03), f"{year}\n{label}", ha="center", va="bottom" if above else "top", fontsize=9.5, color=COLORS["dark"])
    ax.text(0.50, 0.08, "从单算法求解 → 动态重规划 → 自动算法选择 → 多智能体科研闭环", ha="center", fontsize=14, fontweight="bold", color=COLORS["dark"])
    save(fig, "图1-2_路径规划与AI_Scientist技术演进图.png")


def fig_2_1():
    fig, ax = canvas(figsize=(12, 8), title="系统总体分层架构")
    layers = [
        ("表示层", "Streamlit GUI｜地图预览｜路径动画｜结果图表｜报告导出", "#E8F0F7", COLORS["blue"]),
        ("接口层", "FastAPI：/health｜/analyze｜/experiment｜/report", "#E8F0F7", COLORS["blue"]),
        ("智能体编排层", "Orchestrator｜ResearchState｜Human-in-the-loop｜Experiment/Reflection", "#E7F3EF", COLORS["cyan"]),
        ("算法与评估层", "A*｜ACO｜PSO｜SA｜混合优化｜Metrics｜Scoring｜Rules", "#FCECCF", COLORS["orange"]),
        ("知识与数据层", "算法画像｜历史先验｜文献知识库｜SQLite｜地图｜日志", "#E7DFF1", COLORS["purple"]),
        ("基础服务层", "Qwen 兼容接口｜NumPy/SciPy｜文件系统｜配置与日志", "#F8E2E2", COLORS["red"]),
    ]
    for i, (name, details, fc, ec) in enumerate(layers):
        y = 0.80 - i * 0.13
        box(ax, (0.08, y), (0.16, 0.085), name, fc=ec, ec=ec, fontsize=12, weight="bold", text_color="white")
        box(ax, (0.26, y), (0.66, 0.085), details, fc=fc, ec=ec, fontsize=11)
        if i < len(layers) - 1:
            arrow(ax, (0.59, y), (0.59, y - 0.04), COLORS["gray"])
    save(fig, "图2-1_系统总体分层架构图.png")


def fig_2_2():
    fig, ax = canvas(figsize=(13, 8), title="系统功能模块组成")
    box(ax, (0.38, 0.80), (0.24, 0.10), "路径规划虚拟仿真闭环\nAI 科学家系统", fc=COLORS["dark"], ec=COLORS["dark"], fontsize=14, weight="bold", text_color="white")
    groups = [
        (0.03, 0.54, "agents", ["输入/地图分析", "环境与知识", "规则/评估/决策", "假设/反思/人审"], COLORS["cyan"]),
        (0.23, 0.54, "algorithms", ["A*", "ACO", "PSO", "SA / Hybrid"], COLORS["orange"]),
        (0.43, 0.54, "evaluation", ["Benchmark", "Metrics", "Scoring", "ExperimentRunner"], COLORS["green"]),
        (0.63, 0.54, "data / map", ["地图生成解析", "连通性", "SQLite", "日志/数据卡"], COLORS["blue"]),
        (0.83, 0.54, "gui / api", ["Streamlit", "Plotly", "FastAPI", "报告导出"], COLORS["purple"]),
    ]
    for x, y, name, children, color in groups:
        box(ax, (x, y), (0.14, 0.10), name, fc=color, ec=color, weight="bold", text_color="white")
        arrow(ax, (0.50, 0.80), (x + 0.07, y + 0.10), color)
        for j, child in enumerate(children):
            cy = 0.41 - j * 0.095
            box(ax, (x, cy), (0.14, 0.07), child, fc="#FFFFFF", ec=color, fontsize=9.5)
            arrow(ax, (x + 0.07, y), (x + 0.07, cy + 0.07), color, width=1.0)
    save(fig, "图2-2_系统功能模块组成图.png")


def fig_2_3():
    fig, ax = canvas(figsize=(13, 7), title="ResearchState 数据流")
    stages = [
        ("env_input", "环境参数\n起终点/算力", COLORS["blue"]),
        ("map_features", "聚类/瓶颈\n熵/距离", COLORS["cyan"]),
        ("knowledge", "文献事实\n历史记录", COLORS["purple"]),
        ("evaluation", "指标/规则\n得分/排名", COLORS["orange"]),
        ("decision", "推荐/置信度\n人工审核", COLORS["red"]),
        ("research", "假设/实验\n反思/参数", COLORS["green"]),
    ]
    for i, (key, detail, color) in enumerate(stages):
        x = 0.03 + i * 0.16
        box(ax, (x, 0.55), (0.13, 0.18), f"{key}\n\n{detail}", fc="#FFFFFF", ec=color, fontsize=10.5, weight="bold")
        if i < len(stages) - 1:
            arrow(ax, (x + 0.13, 0.64), (x + 0.16, 0.64), COLORS["gray"])
    box(ax, (0.24, 0.24), (0.52, 0.14), "metadata：智能体 I/O、错误记录、迭代次数、收敛状态、人工反馈", fc=COLORS["light"], ec=COLORS["gray"], fontsize=12)
    for i in range(6):
        x = 0.095 + i * 0.16
        arrow(ax, (x, 0.55), (0.42 + 0.03 * i, 0.38), COLORS["gray"], style="->", width=1.0)
    save(fig, "图2-3_ResearchState数据流图.png")


def fig_2_4():
    fig, ax = canvas(figsize=(12, 8), title="AI Scientist 完整闭环")
    nodes = [
        (0.43, 0.78, "问题与环境输入", COLORS["blue"]),
        (0.70, 0.65, "地图/环境分析", COLORS["cyan"]),
        (0.76, 0.39, "知识检索与规则", COLORS["purple"]),
        (0.58, 0.16, "评分与算法决策", COLORS["orange"]),
        (0.28, 0.16, "实验执行与评估", COLORS["green"]),
        (0.09, 0.39, "反思与人审", COLORS["red"]),
        (0.15, 0.65, "假设与计划修订", COLORS["purple"]),
    ]
    centers = []
    for x, y, label, color in nodes:
        box(ax, (x, y), (0.17, 0.10), label, fc=color, ec=color, fontsize=11, weight="bold", text_color="white")
        centers.append((x + 0.085, y + 0.05))
    for i in range(len(centers)):
        arrow(ax, centers[i], centers[(i + 1) % len(centers)], COLORS["dark"], connectionstyle="arc3,rad=0.10")
    box(ax, (0.39, 0.40), (0.22, 0.14), "ResearchState\n统一研究状态", fc="#FFFFFF", ec=COLORS["dark"], fontsize=13, weight="bold")
    for center in centers:
        arrow(ax, center, (0.50, 0.47), COLORS["gray"], style="->", width=0.8)
    ax.text(0.5, 0.07, "最多三轮迭代｜反思置信度 ≥ 0.7 时收敛｜结果与知识可追溯", ha="center", fontsize=12, color=COLORS["dark"])
    save(fig, "图2-4_AI_Scientist完整闭环流程图.png")


def fig_2_5():
    fig, ax = canvas(figsize=(12, 7), title="异常隔离与降级决策")
    box(ax, (0.06, 0.72), (0.18, 0.10), "智能体步骤执行", fc=COLORS["blue"], ec=COLORS["blue"], weight="bold", text_color="white")
    box(ax, (0.35, 0.72), (0.18, 0.10), "执行是否成功？", fc="#FFFFFF", ec=COLORS["dark"], weight="bold")
    arrow(ax, (0.24, 0.77), (0.35, 0.77))
    box(ax, (0.70, 0.72), (0.20, 0.10), "更新 ResearchState", fc=COLORS["green"], ec=COLORS["green"], weight="bold", text_color="white")
    arrow(ax, (0.53, 0.77), (0.70, 0.77), COLORS["green"])
    ax.text(0.61, 0.80, "是", fontsize=10, color=COLORS["green"])
    box(ax, (0.35, 0.48), (0.18, 0.10), "记录错误并保留旧状态", fc="#F8E2E2", ec=COLORS["red"], fontsize=10.5, weight="bold")
    arrow(ax, (0.44, 0.72), (0.44, 0.58), COLORS["red"])
    ax.text(0.46, 0.64, "否", fontsize=10, color=COLORS["red"])
    box(ax, (0.06, 0.26), (0.20, 0.10), "LLM 服务可用？", fc="#FFFFFF", ec=COLORS["purple"], weight="bold")
    box(ax, (0.36, 0.26), (0.20, 0.10), "Qwen 生成解释/假设", fc="#E7DFF1", ec=COLORS["purple"], fontsize=10.5)
    box(ax, (0.70, 0.26), (0.20, 0.10), "模板化离线回退", fc="#FCECCF", ec=COLORS["orange"], fontsize=10.5)
    arrow(ax, (0.26, 0.31), (0.36, 0.31), COLORS["purple"])
    arrow(ax, (0.16, 0.26), (0.70, 0.31), COLORS["orange"], connectionstyle="arc3,rad=-0.20")
    ax.text(0.30, 0.34, "是", fontsize=10, color=COLORS["purple"])
    ax.text(0.45, 0.18, "否", fontsize=10, color=COLORS["orange"])
    box(ax, (0.36, 0.06), (0.20, 0.09), "算法决策仍由数据与规则完成", fc=COLORS["dark"], ec=COLORS["dark"], fontsize=10.5, weight="bold", text_color="white")
    arrow(ax, (0.46, 0.26), (0.46, 0.15))
    arrow(ax, (0.80, 0.26), (0.56, 0.11))
    save(fig, "图2-5_异常隔离与降级决策流程图.png")


def fig_3_1():
    fig, ax = canvas(figsize=(11, 7), title="栅格路径规划问题模型")
    n = 12
    for i in range(n + 1):
        ax.plot([0.08, 0.68], [0.17 + i * 0.05, 0.17 + i * 0.05], color="#CDD6DE", linewidth=0.6)
        ax.plot([0.08 + i * 0.05, 0.08 + i * 0.05], [0.17, 0.77], color="#CDD6DE", linewidth=0.6)
    obstacles = [(2, 2), (3, 2), (6, 2), (7, 2), (7, 3), (4, 5), (5, 5), (6, 5), (2, 8), (3, 8), (8, 8), (9, 8), (9, 9)]
    for x, y in obstacles:
        ax.add_patch(Rectangle((0.08 + x * 0.05, 0.17 + y * 0.05), 0.05, 0.05, facecolor=COLORS["dark"]))
    path = [(0, 0), (1, 0), (1, 1), (2, 1), (3, 1), (4, 1), (4, 2), (4, 3), (5, 3), (6, 3), (6, 4), (7, 4), (8, 4), (8, 5), (8, 6), (9, 6), (10, 6), (10, 7), (10, 8), (10, 9), (11, 9), (11, 10), (11, 11)]
    xs = [0.105 + x * 0.05 for x, y in path]
    ys = [0.195 + y * 0.05 for x, y in path]
    ax.plot(xs, ys, color=COLORS["cyan"], linewidth=3)
    ax.scatter([xs[0], xs[-1]], [ys[0], ys[-1]], s=110, c=[COLORS["green"], COLORS["red"]], zorder=5)
    box(ax, (0.75, 0.60), (0.18, 0.10), "状态空间 V\n可通行栅格", fc="#E8F0F7", ec=COLORS["blue"])
    box(ax, (0.75, 0.43), (0.18, 0.10), "边集合 E\n四邻域移动", fc="#E7F3EF", ec=COLORS["cyan"])
    box(ax, (0.75, 0.26), (0.18, 0.10), "目标\n最小代价可行路径", fc="#FCECCF", ec=COLORS["orange"])
    ax.text(0.38, 0.10, "黑色：障碍物　绿色：起点　红色：终点　青色：可行路径", ha="center", fontsize=11)
    save(fig, "图3-1_栅格地图与可行路径问题模型.png")


def fig_3_2():
    fig, ax = canvas(figsize=(13, 8), title="五类路径规划算法处理流程对比")
    rows = [
        ("A*", ["开放集合", "f=g+h", "扩展最优节点", "回溯路径"], COLORS["blue"]),
        ("ACO", ["初始化信息素", "蚂蚁概率游走", "筛选可行路径", "挥发与沉积"], COLORS["orange"]),
        ("PSO 原型", ["随机贪心路径", "个体/全局最优", "交叉与变异", "更新候选路径"], COLORS["green"]),
        ("SA", ["生成初始路径", "邻域扰动", "概率接受", "温度下降"], COLORS["red"]),
        ("Hybrid", ["A* 初始路径", "视线检测", "删除冗余节点", "输出平滑路径"], COLORS["purple"]),
    ]
    for i, (name, steps, color) in enumerate(rows):
        y = 0.77 - i * 0.145
        box(ax, (0.03, y), (0.12, 0.08), name, fc=color, ec=color, weight="bold", text_color="white")
        for j, step in enumerate(steps):
            x = 0.20 + j * 0.19
            box(ax, (x, y), (0.15, 0.08), step, fc="#FFFFFF", ec=color, fontsize=10)
            if j < 3:
                arrow(ax, (x + 0.15, y + 0.04), (x + 0.19, y + 0.04), color)
    ax.text(0.50, 0.07, "注：项目 PSO 为路径交叉/变异原型，不等同于标准连续速度—位置更新", ha="center", fontsize=11, color=COLORS["red"])
    save(fig, "图3-2_五类路径规划算法处理流程对比图.png")


def fig_3_3():
    fig, ax = canvas(figsize=(12, 7), title="场景评分与算法选型决策流程")
    labels = [
        (0.04, "地图与环境\n特征", COLORS["blue"]),
        (0.22, "复杂度分类\n低/中/高", COLORS["cyan"]),
        (0.40, "九维指标\n归一化", COLORS["green"]),
        (0.58, "场景权重\n加权求和", COLORS["orange"]),
        (0.76, "规则惩罚\n与约束", COLORS["red"]),
    ]
    for i, (x, label, color) in enumerate(labels):
        box(ax, (x, 0.57), (0.15, 0.14), label, fc="#FFFFFF", ec=color, fontsize=11, weight="bold")
        if i < len(labels) - 1:
            arrow(ax, (x + 0.15, 0.64), (x + 0.18, 0.64), COLORS["gray"])
    box(ax, (0.34, 0.29), (0.30, 0.13), "算法排名 + 置信度 + 决策解释", fc=COLORS["dark"], ec=COLORS["dark"], fontsize=13, weight="bold", text_color="white")
    arrow(ax, (0.835, 0.57), (0.64, 0.36), COLORS["dark"])
    box(ax, (0.08, 0.10), (0.25, 0.10), "分差过小 / 知识不足 / 低成功率", fc="#F8E2E2", ec=COLORS["red"], fontsize=10.5)
    box(ax, (0.67, 0.10), (0.25, 0.10), "自动推荐算法与参数", fc="#E7F3EF", ec=COLORS["green"], fontsize=11, weight="bold")
    arrow(ax, (0.42, 0.29), (0.25, 0.20), COLORS["red"])
    arrow(ax, (0.58, 0.29), (0.79, 0.20), COLORS["green"])
    box(ax, (0.35, 0.08), (0.30, 0.10), "触发人工审核并允许偏好反馈", fc="#FCECCF", ec=COLORS["orange"], fontsize=11)
    arrow(ax, (0.33, 0.15), (0.35, 0.13), COLORS["orange"])
    save(fig, "图3-3_场景评分与算法选型决策流程图.png")


def fig_3_4():
    fig, ax = canvas(figsize=(12, 7), title="算法参数推荐与偏好约束")
    prefs = [("速度优先", COLORS["blue"]), ("路径优先", COLORS["green"]), ("成功率优先", COLORS["red"]), ("均衡模式", COLORS["purple"])]
    for i, (label, color) in enumerate(prefs):
        box(ax, (0.04, 0.72 - i * 0.16), (0.15, 0.09), label, fc=color, ec=color, weight="bold", text_color="white")
        arrow(ax, (0.19, 0.765 - i * 0.16), (0.39, 0.52), color)
    box(ax, (0.37, 0.39), (0.24, 0.25), "ParameterAgent\n\n场景等级\n算力限制\n优化偏好\n推荐算法", fc="#FFFFFF", ec=COLORS["dark"], fontsize=12, weight="bold")
    outputs = ["ACO：蚂蚁数/迭代数", "PSO：粒子数/迭代数", "SA：温度/冷却率", "Hybrid：平滑次数"]
    for i, label in enumerate(outputs):
        y = 0.72 - i * 0.16
        box(ax, (0.72, y), (0.23, 0.09), label, fc="#FCECCF", ec=COLORS["orange"], fontsize=10.5)
        arrow(ax, (0.61, 0.52), (0.72, y + 0.045), COLORS["orange"])
    ax.text(0.50, 0.12, "输出参数必须受计算预算和算法白名单约束；推荐结果可由人工偏好再次修订", ha="center", fontsize=11.5)
    save(fig, "图3-4_算法参数推荐与偏好约束关系图.png")


def fig_4_1():
    fig, ax = canvas(figsize=(13, 8), title="多智能体角色分组与协作关系")
    groups = [
        (0.03, 0.57, "输入感知", ["DataReceiver", "MapAnalysis", "Environment"], COLORS["blue"]),
        (0.23, 0.57, "知识增强", ["Literature", "FactExtraction", "KnowledgeRetrieval"], COLORS["purple"]),
        (0.43, 0.57, "决策评估", ["RuleConstraint", "AlgorithmEvaluation", "Decision"], COLORS["orange"]),
        (0.63, 0.57, "科研生成", ["Explanation", "Hypothesis", "Experiment", "Reflection"], COLORS["green"]),
        (0.83, 0.57, "监督控制", ["HumanLoop", "Parameter", "Orchestrator"], COLORS["red"]),
    ]
    for x, y, name, children, color in groups:
        box(ax, (x, y), (0.14, 0.11), name, fc=color, ec=color, weight="bold", text_color="white")
        for j, child in enumerate(children):
            cy = 0.43 - j * 0.10
            box(ax, (x, cy), (0.14, 0.065), child, fc="#FFFFFF", ec=color, fontsize=8.5)
            arrow(ax, (x + 0.07, y), (x + 0.07, cy + 0.065), color, style="->", width=0.8)
    for i in range(4):
        x1 = groups[i][0] + 0.14
        x2 = groups[i + 1][0]
        arrow(ax, (x1, 0.625), (x2, 0.625), COLORS["dark"])
    box(ax, (0.35, 0.08), (0.30, 0.11), "ResearchState 统一共享状态", fc=COLORS["dark"], ec=COLORS["dark"], fontsize=13, weight="bold", text_color="white")
    for x, *_ in groups:
        arrow(ax, (x + 0.07, 0.24), (0.50, 0.19), COLORS["gray"], style="->", width=0.8)
    save(fig, "图4-1_多智能体角色分组与协作关系图.png")


def fig_4_2():
    fig, ax = canvas(figsize=(14, 8), title="OrchestratorAgent 顺序编排时序")
    agents = ["数据", "地图", "环境", "文献", "事实", "知识", "规则", "评估", "决策", "人审", "解释", "假设", "反思", "参数"]
    colors = [COLORS["blue"]] * 3 + [COLORS["purple"]] * 3 + [COLORS["orange"]] * 3 + [COLORS["red"]] + [COLORS["green"]] * 4
    for i, (name, color) in enumerate(zip(agents, colors)):
        x = 0.025 + i * 0.069
        box(ax, (x, 0.79), (0.055, 0.075), name, fc=color, ec=color, fontsize=8.5, weight="bold", text_color="white", radius=0.012)
        ax.plot([x + 0.0275, x + 0.0275], [0.20, 0.79], color="#BBC5CD", linestyle="--", linewidth=0.8)
        if i < len(agents) - 1:
            y = 0.72 - (i % 5) * 0.09
            arrow(ax, (x + 0.0275, y), (x + 0.096, y), color, width=1.0)
            ax.text(x + 0.061, y + 0.015, f"S{i+1}", ha="center", fontsize=7)
    box(ax, (0.30, 0.08), (0.40, 0.09), "_safe_step：异常写入 metadata，保留已有状态并继续后续步骤", fc="#F8E2E2", ec=COLORS["red"], fontsize=11)
    save(fig, "图4-2_OrchestratorAgent顺序编排时序图.png")


def fig_4_3():
    fig, ax = canvas(figsize=(12, 7), title="文献—知识库—RAG 增强链路")
    sources = [("外部文献元数据", COLORS["blue"]), ("literature_kb.json", COLORS["purple"]), ("algorithm_profile.json", COLORS["orange"]), ("historical_results.json", COLORS["green"]), ("experiments.sqlite", COLORS["red"])]
    for i, (name, color) in enumerate(sources):
        y = 0.77 - i * 0.13
        box(ax, (0.04, y), (0.20, 0.08), name, fc="#FFFFFF", ec=color, fontsize=10)
        arrow(ax, (0.24, y + 0.04), (0.39, 0.52), color)
    box(ax, (0.37, 0.38), (0.22, 0.25), "检索与事实处理\n\nLiteratureAgent\nFactExtractionAgent\nKnowledgeRetrievalAgent\nRAGAgent", fc="#E7DFF1", ec=COLORS["purple"], fontsize=11, weight="bold")
    box(ax, (0.70, 0.63), (0.23, 0.10), "可核验文献事实", fc="#E8F0F7", ec=COLORS["blue"], weight="bold")
    box(ax, (0.70, 0.43), (0.23, 0.10), "候选算法历史表现", fc="#E7F3EF", ec=COLORS["green"], weight="bold")
    box(ax, (0.70, 0.23), (0.23, 0.10), "解释、假设与反思上下文", fc="#FCECCF", ec=COLORS["orange"], weight="bold")
    for y in [0.68, 0.48, 0.28]:
        arrow(ax, (0.59, 0.505), (0.70, y), COLORS["gray"])
    ax.text(0.50, 0.09, "实现边界：RAGAgent 当前尚未进入 Orchestrator 主链路，报告不将设计能力误写为已完全贯通", ha="center", fontsize=10.5, color=COLORS["red"])
    save(fig, "图4-3_文献知识库RAG增强链路图.png")


def fig_4_4():
    fig, ax = canvas(figsize=(12, 8), title="假设—实验—反思—人在回路闭环")
    nodes = [
        (0.39, 0.77, "生成可检验假设", COLORS["purple"]),
        (0.68, 0.58, "构造实验方案", COLORS["blue"]),
        (0.68, 0.29, "五算法虚拟仿真", COLORS["green"]),
        (0.39, 0.10, "结果汇总与支持度", COLORS["orange"]),
        (0.10, 0.29, "ReflectionAgent", COLORS["red"]),
        (0.10, 0.58, "HumanLoopAgent", COLORS["red"]),
    ]
    centers = []
    for x, y, text, color in nodes:
        box(ax, (x, y), (0.20, 0.10), text, fc=color, ec=color, weight="bold", text_color="white")
        centers.append((x + 0.10, y + 0.05))
    for i in range(len(centers)):
        arrow(ax, centers[i], centers[(i + 1) % len(centers)], COLORS["dark"], connectionstyle="arc3,rad=0.10")
    box(ax, (0.40, 0.40), (0.20, 0.13), "收敛条件\nconfidence ≥ 0.7\n最多三轮", fc="#FFFFFF", ec=COLORS["dark"], fontsize=12, weight="bold")
    ax.text(0.50, 0.05, "当假设未获支持或人审提出质疑时，修订实验计划并进入下一轮", ha="center", fontsize=11)
    save(fig, "图4-4_假设实验反思人在回路闭环图.png")


def fig_5_1():
    fig, ax = canvas(figsize=(12, 7), title="GUI、API 与核心服务部署关系")
    box(ax, (0.05, 0.65), (0.20, 0.12), "用户浏览器\nStreamlit 页面", fc=COLORS["blue"], ec=COLORS["blue"], fontsize=12, weight="bold", text_color="white")
    box(ax, (0.05, 0.32), (0.20, 0.12), "外部客户端\nHTTP/JSON", fc="#E8F0F7", ec=COLORS["blue"], fontsize=12, weight="bold")
    box(ax, (0.36, 0.65), (0.22, 0.12), "Streamlit GUI\n地图/图表/下载", fc=COLORS["cyan"], ec=COLORS["cyan"], fontsize=12, weight="bold", text_color="white")
    box(ax, (0.36, 0.32), (0.22, 0.12), "FastAPI 服务\n分析/实验/报告", fc=COLORS["purple"], ec=COLORS["purple"], fontsize=12, weight="bold", text_color="white")
    box(ax, (0.69, 0.56), (0.25, 0.20), "核心 Python 服务\n\n多智能体编排\n五算法与评估\n地图与知识库", fc="#FFFFFF", ec=COLORS["dark"], fontsize=12, weight="bold")
    box(ax, (0.69, 0.24), (0.25, 0.15), "持久化与外部服务\nSQLite / JSON / 日志\nQwen 兼容 API", fc="#FCECCF", ec=COLORS["orange"], fontsize=11.5)
    arrow(ax, (0.25, 0.71), (0.36, 0.71), COLORS["blue"])
    arrow(ax, (0.25, 0.38), (0.36, 0.38), COLORS["blue"])
    arrow(ax, (0.58, 0.71), (0.69, 0.66), COLORS["cyan"])
    arrow(ax, (0.58, 0.38), (0.69, 0.61), COLORS["purple"])
    arrow(ax, (0.82, 0.56), (0.82, 0.39), COLORS["orange"])
    arrow(ax, (0.75, 0.39), (0.75, 0.56), COLORS["orange"])
    ax.text(0.50, 0.10, "GUI 当前使用简化决策链；API /analyze 调用完整 Orchestrator", ha="center", fontsize=11, color=COLORS["red"])
    save(fig, "图5-1_GUI_API与核心服务部署关系图.png")


def fig_5_3():
    fig, ax = canvas(figsize=(12, 7), title="SQLite 实验数据库实体关系")
    entities = [
        (0.05, 0.45, "maps", ["PK map_id", "source / map_type", "width / height", "obstacle_ratio", "dynamic_change_rate"], COLORS["blue"]),
        (0.38, 0.38, "algorithm_runs", ["PK run_id", "FK map_id", "algorithm / parameters", "runtime / path_length", "success / metrics", "seed / created_at"], COLORS["orange"]),
        (0.74, 0.45, "hypotheses", ["PK hypothesis_id", "scene_condition", "hypothesis_text", "evidence", "validation_status"], COLORS["purple"]),
    ]
    for x, y, name, fields, color in entities:
        h = 0.10 + len(fields) * 0.055
        box(ax, (x, y), (0.22, h), "", fc="#FFFFFF", ec=color)
        ax.add_patch(Rectangle((x, y + h - 0.08), 0.22, 0.08, facecolor=color, edgecolor=color))
        ax.text(x + 0.11, y + h - 0.04, name, ha="center", va="center", color="white", fontsize=12, fontweight="bold")
        for j, field in enumerate(fields):
            ax.text(x + 0.02, y + h - 0.115 - j * 0.055, field, ha="left", va="center", fontsize=9.5, color=COLORS["dark"])
    arrow(ax, (0.27, 0.60), (0.38, 0.60), COLORS["dark"], style="-|>")
    ax.text(0.325, 0.63, "1 : N", ha="center", fontsize=10)
    arrow(ax, (0.60, 0.51), (0.74, 0.57), COLORS["gray"], style="->", connectionstyle="arc3,rad=-0.15")
    ax.text(0.67, 0.58, "实验验证", ha="center", fontsize=9)
    ax.text(0.50, 0.12, "现有数据库用于原型运行记录；正式报告采用第 8 步独立原始数据与汇总文件", ha="center", fontsize=11, color=COLORS["red"])
    save(fig, "图5-3_SQLite实验数据库实体关系图.png")


def main():
    functions = [
        fig_1_1, fig_1_2,
        fig_2_1, fig_2_2, fig_2_3, fig_2_4, fig_2_5,
        fig_3_1, fig_3_2, fig_3_3, fig_3_4,
        fig_4_1, fig_4_2, fig_4_3, fig_4_4,
        fig_5_1, fig_5_3,
    ]
    for index, func in enumerate(functions, 1):
        func()
        print(f"[{index}/{len(functions)}] {func.__name__}")


if __name__ == "__main__":
    main()
