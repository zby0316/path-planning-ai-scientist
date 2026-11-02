# gui/visualization.py — 图表绘制工具（Phase 1 Plotly 升级 + Phase 2 高级可视化）

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from agents.explanation_agent import ExplanationAgent
from agents.hypothesis_agent import HypothesisAgent


# ========== 全局 matplotlib 中文配置（兼容旧代码残留） ==========
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DengXian", "PingFang SC"]
plt.rcParams["axes.unicode_minus"] = False  # 正常显示负号
# ============================================================


# ========== Phase 1：核心三件套的 Plotly 重写 ==========

def draw_grid(grid: np.ndarray, path: list = None, start: tuple = None, target: tuple = None, title: str = "地图可视化"):
    """Plotly 版本：绘制栅格地图与路径。Heatmap 使用次坐标轴 xaxis2/yaxis2，Scatter 使用主坐标轴。"""
    fig = go.Figure()

    h, w = grid.shape

    # 背景 Heatmap（绑定到次坐标轴，与 Scatter 坐标分离）
    fig.add_trace(go.Heatmap(
        z=grid,
        colorscale=[[0, "white"], [1, "black"]],
        showscale=False,
        hoverinfo="skip",
        zmin=0,
        zmax=1,
        xaxis="x2",
        yaxis="y2",
    ))

    # 起点
    if start is not None:
        sx, sy = start[0], start[1]
        fig.add_trace(go.Scatter(
            x=[sx], y=[sy],
            mode="markers",
            marker=dict(symbol="star", size=15, color="green"),
            name="起点",
            hovertemplate="起点 (%{x}, %{y})<extra></extra>",
        ))

    # 终点
    if target is not None:
        tx, ty = target[0], target[1]
        fig.add_trace(go.Scatter(
            x=[tx], y=[ty],
            mode="markers",
            marker=dict(symbol="star", size=15, color="red"),
            name="终点",
            hovertemplate="终点 (%{x}, %{y})<extra></extra>",
        ))

    # 路径（仅当 path 非空）
    if path:
        xs = [p[0] for p in path]
        ys = [p[1] for p in path]
        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode="lines+markers",
            line=dict(color="blue", width=2),
            marker=dict(size=4),
            name="路径",
            hovertemplate="路径 (%{x}, %{y})<extra></extra>",
        ))

    # layout：y 轴反转匹配 grid 数组方向；xaxis2/yaxis2 overlay 主轴用于 Heatmap
    fig.update_layout(
        title=title,
        height=500,
        plot_bgcolor="white",
        xaxis=dict(
            range=[-0.5, w - 0.5],
            showgrid=False,
            zeroline=False,
            constrain="domain",
        ),
        yaxis=dict(
            range=[h - 0.5, -0.5],
            autorange="reversed",
            showgrid=False,
            zeroline=False,
        ),
        xaxis2=dict(
            overlaying="x",
            range=[-0.5, w - 0.5],
            showgrid=False,
            zeroline=False,
        ),
        yaxis2=dict(
            overlaying="y",
            range=[h - 0.5, -0.5],
            showgrid=False,
            zeroline=False,
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def draw_ranking_bar(ranking: list):
    """Plotly 版本：算法综合评分柱状图。ranking 元素含 algorithm + score 字段。"""
    fig = go.Figure()
    x = [r["algorithm"] for r in ranking]
    y = [r["score"] for r in ranking]
    colors = ["#2ecc71" if i == 0 else "#3498db" for i in range(len(ranking))]
    fig.add_trace(go.Bar(
        x=x,
        y=y,
        marker_color=colors,
        text=[f"{s:.3f}" for s in y],
        textposition="outside",
        hovertemplate="%{x}<br>得分: %{y:.4f}<extra></extra>",
    ))
    fig.update_layout(
        title="算法综合评分排名",
        yaxis=dict(range=[0, 1]),
        height=400,
        showlegend=False,
        plot_bgcolor="white",
    )
    return fig


def draw_radar(ranking: list):
    """Plotly 版本：4 维雷达图（耗时/路径长度/成功率/稳定性）。ranking 元素 detail 含 4 个 _score 字段。"""
    categories = ["耗时", "路径长度", "成功率", "稳定性"]
    fig = go.Figure()
    palette = ["#2ecc71", "#3498db", "#e74c3c", "#f39c12", "#9b59b6"]
    for idx, r in enumerate(ranking[:5]):
        detail = r.get("detail", {})
        values = [
            detail.get("time_score", 0),
            detail.get("length_score", 0),
            detail.get("success_score", 0),
            detail.get("stability_score", 0),
        ]
        values += values[:1]
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill="toself",
            opacity=0.5,
            line=dict(color=palette[idx % len(palette)], width=2),
            name=r.get("algorithm", f"算法{idx+1}"),
            hovertemplate="%{theta}: %{r:.3f}<extra>%{fullData.name}</extra>",
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(range=[0, 1], visible=True)),
        title="多指标雷达对比",
        height=500,
    )
    return fig


# ========== Phase 2：高级可视化组件 ==========

def draw_multi_path_overlay(grid, paths: dict, start, target):
    """在栅格地图上叠加多条算法路径，便于直观对比。"""
    color_map = {
        "A*": "#e74c3c",
        "ACO": "#3498db",
        "PSO": "#2ecc71",
        "SA": "#f39c12",
        "混合优化算法": "#9b59b6",
    }
    fig = go.Figure()

    h, w = grid.shape
    fig.add_trace(go.Heatmap(
        z=grid,
        colorscale=[[0, "white"], [1, "black"]],
        showscale=False,
        hoverinfo="skip",
        zmin=0,
        zmax=1,
        xaxis="x2",
        yaxis="y2",
    ))

    if start is not None:
        fig.add_trace(go.Scatter(
            x=[start[0]], y=[start[1]],
            mode="markers",
            marker=dict(symbol="star", size=15, color="green"),
            name="起点",
            hovertemplate="起点 (%{x}, %{y})<extra></extra>",
        ))
    if target is not None:
        fig.add_trace(go.Scatter(
            x=[target[0]], y=[target[1]],
            mode="markers",
            marker=dict(symbol="star", size=15, color="red"),
            name="终点",
            hovertemplate="终点 (%{x}, %{y})<extra></extra>",
        ))

    for algo, path in paths.items():
        if not path:
            continue
        xs = [p[0] for p in path]
        ys = [p[1] for p in path]
        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode="lines",
            line=dict(color=color_map.get(algo, "#7f8c8d"), width=2),
            name=algo,
            hovertemplate="%{fullData.name} (%{x}, %{y})<extra></extra>",
        ))

    fig.update_layout(
        title="多算法路径叠加对比",
        height=500,
        plot_bgcolor="white",
        xaxis=dict(range=[-0.5, w - 0.5], showgrid=False, zeroline=False),
        yaxis=dict(range=[h - 0.5, -0.5], autorange="reversed", showgrid=False, zeroline=False),
        xaxis2=dict(overlaying="x", range=[-0.5, w - 0.5], showgrid=False, zeroline=False),
        yaxis2=dict(overlaying="y", range=[h - 0.5, -0.5], showgrid=False, zeroline=False),
    )
    return fig


def draw_animated_bar_chart(ranking, metrics: list = None):
    """可下拉切换指标维度的多算法对比柱状图（Plotly updatemenus）。"""
    if metrics is None:
        metrics = ["time", "length", "success", "stability", "smoothness", "safety"]

    fig = go.Figure()
    algorithms = [r.get("algorithm", f"算法{i+1}") for i, r in enumerate(ranking)]

    for i, m in enumerate(metrics):
        field = f"{m}_score"
        y_values = [r.get("detail", {}).get(field, 0.0) for r in ranking]
        fig.add_trace(go.Bar(
            x=algorithms,
            y=y_values,
            name=m,
            visible=(i == 0),
            hovertemplate="%{x}<br>" + m + ": %{y:.3f}<extra></extra>",
        ))

    buttons = []
    for i, m in enumerate(metrics):
        visibility = [False] * len(metrics)
        visibility[i] = True
        buttons.append(dict(
            label=m,
            method="update",
            args=[{"visible": visibility}, {"title": f"算法多指标对比 - {m}"}],
        ))

    fig.update_layout(
        title="算法多指标对比（点击下拉切换）",
        height=450,
        showlegend=True,
        barmode="group",
        yaxis=dict(range=[0, 1.1]),
        updatemenus=[dict(
            buttons=buttons,
            direction="down",
            showactive=True,
            x=1.15,
            y=1.0,
        )],
        plot_bgcolor="white",
    )
    return fig


def draw_extended_radar(ranking, metrics_10: list = None):
    """九项评分指标雷达图，不把惩罚或重复字段作为维度。"""
    if metrics_10 is None:
        metrics_10 = [
            "time_score", "length_score", "success_score", "stability_score",
            "smoothness_score", "safety_score_score", "expanded_nodes_score",
            "compute_cost_score", "robustness_score",
        ]
    labels = [
        "耗时", "路径长度", "成功率", "稳定性", "平滑度",
        "安全性", "搜索效率", "计算代价", "鲁棒性",
    ]
    colors = ["#2ecc71", "#3498db", "#e74c3c", "#f39c12", "#9b59b6"]
    fig = go.Figure()
    for idx, r in enumerate(ranking[:5]):
        detail = r.get("detail", {})
        values = [detail.get(m, 0.0) for m in metrics_10]
        values += values[:1]
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=labels + [labels[0]],
            fill="toself",
            opacity=0.5,
            line=dict(color=colors[idx % len(colors)], width=2),
            name=r.get("algorithm", f"算法{idx+1}"),
            hovertemplate="%{theta}: %{r:.3f}<extra>%{fullData.name}</extra>",
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(range=[0, 1], visible=True)),
        title="9 维扩展雷达对比",
        height=500,
    )
    return fig


def highlight_pareto_front(ranking):
    """高亮 Pareto 前沿：以 avg_time / avg_path_length 为两轴，非支配解标红星号。"""
    fig = go.Figure()
    if not ranking:
        fig.update_layout(
            title="Pareto 前沿高亮（耗时 vs 路径长度）",
            xaxis_title="平均耗时 (s)",
            yaxis_title="平均路径长度",
            height=450,
        )
        return fig

    valid = [r for r in ranking if "avg_time" in r and "avg_path_length" in r]
    if not valid:
        fig.update_layout(
            title="Pareto 前沿高亮（耗时 vs 路径长度）- 数据不足",
            xaxis_title="平均耗时 (s)",
            yaxis_title="平均路径长度",
            height=450,
        )
        return fig

    pareto_mask = []
    for i, ri in enumerate(valid):
        dominated = False
        for j, rj in enumerate(valid):
            if i == j:
                continue
            t_ok = rj["avg_time"] <= ri["avg_time"]
            l_ok = rj["avg_path_length"] <= ri["avg_path_length"]
            if t_ok and l_ok and (
                rj["avg_time"] < ri["avg_time"] or rj["avg_path_length"] < ri["avg_path_length"]
            ):
                dominated = True
                break
        pareto_mask.append(not dominated)

    pareto_pts = [(valid[i]["algorithm"], valid[i]["avg_time"], valid[i]["avg_path_length"])
                  for i in range(len(valid)) if pareto_mask[i]]
    other_pts = [(valid[i]["algorithm"], valid[i]["avg_time"], valid[i]["avg_path_length"])
                 for i in range(len(valid)) if not pareto_mask[i]]

    if other_pts:
        fig.add_trace(go.Scatter(
            x=[p[1] for p in other_pts],
            y=[p[2] for p in other_pts],
            mode="markers",
            marker=dict(symbol="circle", size=10, color="#3498db"),
            name="非最优",
            text=[p[0] for p in other_pts],
            hovertemplate="<b>%{text}</b><br>耗时: %{x:.4f}<br>路径长度: %{y:.2f}<extra></extra>",
        ))
    if pareto_pts:
        fig.add_trace(go.Scatter(
            x=[p[1] for p in pareto_pts],
            y=[p[2] for p in pareto_pts],
            mode="markers",
            marker=dict(symbol="star", size=15, color="#e74c3c"),
            name="Pareto 最优",
            text=[p[0] for p in pareto_pts],
            hovertemplate="<b>%{text}</b><br>耗时: %{x:.4f}<br>路径长度: %{y:.2f}<extra></extra>",
        ))

    fig.update_layout(
        title="Pareto 前沿高亮（耗时 vs 路径长度）",
        xaxis_title="平均耗时 (s)",
        yaxis_title="平均路径长度",
        height=450,
        showlegend=True,
        plot_bgcolor="white",
    )
    return fig


def render_enhanced_reasoning_chain(decision: dict):
    """渲染 7 步推理链，支持一键展开 / 折叠。"""
    import streamlit as st

    if "reasoning_expanded_all" not in st.session_state:
        st.session_state.reasoning_expanded_all = False

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📂 展开全部", use_container_width=True):
            st.session_state.reasoning_expanded_all = True
            st.rerun()
    with col2:
        if st.button("📁 折叠全部", use_container_width=True):
            st.session_state.reasoning_expanded_all = False
            st.rerun()

    steps = [
        {
            "name": "① 数据接收智能体",
            "confidence": 1.0,
            "input": {"env_keys": ["map_width", "map_height", "obstacle_ratio", "compute_limit"]},
            "output": {"validation": "passed", "errors": []},
        },
        {
            "name": "② 环境分析智能体",
            "confidence": 0.95,
            "input": {"grid_analyzed": True},
            "output": {
                "scene_level": decision.get("scene_level", "N/A"),
                "complexity_index": decision.get("complexity_index", "N/A"),
            },
        },
        {
            "name": "③ 知识库检索智能体",
            "confidence": 0.90,
            "input": {"query_scene": decision.get("scene_level", "N/A")},
            "output": {"matched_records": 5},
        },
        {
            "name": "④ 规则约束智能体",
            "confidence": 0.92,
            "input": {"candidate_algorithms": ["A*", "ACO", "PSO", "SA", "混合优化算法"]},
            "output": {"constraints_applied": 3},
        },
        {
            "name": "⑤ 算法评估智能体",
            "confidence": 0.96,
            "input": {"metric_dimensions": 10},
            "output": {"algorithms_scored": 5},
        },
        {
            "name": "⑥ 决策生成智能体",
            "confidence": 0.98,
            "input": {"ranking_size": len(decision.get("ranking", []))},
            "output": {
                "best_algorithm": decision.get("best_algorithm", "N/A"),
                "best_score": decision.get("best_score", 0),
            },
        },
        {
            "name": "⑦ 参数推荐智能体",
            "confidence": 0.90,
            "input": {"best_algorithm": decision.get("best_algorithm", "N/A")},
            "output": {"parameters_recommended": True},
        },
    ]

    for step in steps:
        with st.expander(
            f"{step['name']}  置信度: {step['confidence']:.0%}",
            expanded=st.session_state.reasoning_expanded_all,
        ):
            c1, c2 = st.columns([1, 1])
            with c1:
                st.json(step["input"])
            with c2:
                st.json(step["output"])


def export_pdf_or_fallback(md_content: str, file_name: str) -> tuple:
    """尝试用 pdfkit 导出 PDF，失败时退回 Markdown 字节。"""
    try:
        import pdfkit
        pdf_bytes = pdfkit.from_string(md_content, False)
        return (pdf_bytes, "application/pdf", False)
    except Exception:
        return (md_content.encode("utf-8"), "text/markdown", True)


# ========== Streamlit 渲染与 Plotly 仪表盘辅助函数（保留原版） ==========

_SCENE_LEVEL_COLOR_MAP = {
    "低复杂度": "green",
    "中复杂度": "orange",
    "高复杂度": "red",
    "low": "green",
    "medium": "orange",
    "high": "red",
}


def _resolve_scene_color(scene_level: str) -> str:
    """根据场景等级返回 Streamlit markdown 颜色 token"""
    if scene_level is None:
        return "blue"
    return _SCENE_LEVEL_COLOR_MAP.get(scene_level, "blue")


def _score_color(score: float) -> str:
    if score >= 0.8:
        return "green"
    elif score >= 0.5:
        return "orange"
    else:
        return "red"


def draw_metric_cards(metrics: dict):
    """将指标字典渲染为 Plotly 指标卡片组合图（2x2 布局）"""
    fig = go.Figure()

    keys = list(metrics.keys())[:4]
    positions = {
        0: (0.02, 0.52, 0.46, 0.46),
        1: (0.52, 0.52, 0.46, 0.46),
        2: (0.02, 0.02, 0.46, 0.46),
        3: (0.52, 0.02, 0.46, 0.46),
    }

    for idx, key in enumerate(keys):
        value = metrics[key]
        fig.add_annotation(
            x=positions[idx][0] + positions[idx][2] / 2,
            y=positions[idx][1] + positions[idx][3] - 0.05,
            xref="paper",
            yref="paper",
            text=f"<b>{key}</b>",
            showarrow=False,
            font=dict(size=16, color="#2c3e50"),
        )
        fig.add_annotation(
            x=positions[idx][0] + positions[idx][2] / 2,
            y=positions[idx][1] + positions[idx][3] / 2,
            xref="paper",
            yref="paper",
            text=f"<b>{value}</b>",
            showarrow=False,
            font=dict(size=28, color="#1f77b4"),
        )
        fig.add_shape(
            type="rect",
            xref="paper",
            yref="paper",
            x0=positions[idx][0],
            y0=positions[idx][1],
            x1=positions[idx][0] + positions[idx][2],
            y1=positions[idx][1] + positions[idx][3],
            line=dict(color="#cccccc", width=1),
            fillcolor="rgba(245,245,250,0.6)",
        )

    fig.update_layout(
        title="指标卡片总览",
        showlegend=False,
        xaxis=dict(visible=False, range=[0, 1]),
        yaxis=dict(visible=False, range=[0, 1]),
        margin=dict(l=10, r=10, t=50, b=10),
        height=400,
    )
    return fig


def draw_scene_indicator(scene_level: str, complexity: float):
    """渲染场景等级与复杂度的仪表盘"""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=complexity,
            title={"text": f"场景等级: {scene_level}"},
            gauge={
                "axis": {"range": [0, 1]},
                "bar": {"color": "darkblue"},
                "steps": [
                    {"range": [0, 0.33], "color": "lightgreen"},
                    {"range": [0.33, 0.66], "color": "yellow"},
                    {"range": [0.66, 1.0], "color": "salmon"},
                ],
            },
        )
    )
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=60, b=20))
    return fig


def draw_10d_bar(detail: dict):
    keys = [
        "time_score", "length_score", "success_score", "stability_score",
        "smoothness_score", "safety_score_score", "expanded_nodes_score",
        "compute_cost_score", "robustness_score", "penalty",
    ]
    labels = [
        "耗时", "路径长度", "成功率", "稳定性", "平滑度",
        "安全得分", "扩展节点", "计算开销", "鲁棒性", "惩罚项",
    ]
    values = [detail.get(k, 0) for k in keys]
    colors = []
    for i, (k, v) in enumerate(zip(keys, values)):
        if k == "penalty":
            if v == 0:
                colors.append("#2ecc71")
            elif v < 0.1:
                colors.append("#f39c12")
            else:
                colors.append("#e74c3c")
        else:
            if v >= 0.8:
                colors.append("#2ecc71")
            elif v >= 0.5:
                colors.append("#f39c12")
            else:
                colors.append("#e74c3c")

    fig = go.Figure(
        go.Bar(x=labels, y=values, marker_color=colors, text=[f"{v:.3f}" for v in values], textposition="outside")
    )
    fig.update_layout(
        title="推荐算法 9 项指标与惩罚分解",
        xaxis_title="指标维度",
        yaxis_title="评分",
        yaxis=dict(range=[-1.1, 1.1]) if any(v < 0 for v in values) else dict(range=[0, 1.1]),
        height=450,
        margin=dict(l=40, r=40, t=60, b=80),
    )
    return fig


def draw_10d_radar(ranking: list):
    keys = [
        "time_score", "length_score", "success_score", "stability_score",
        "smoothness_score", "safety_score_score", "expanded_nodes_score",
        "compute_cost_score", "robustness_score",
    ]
    labels = [
        "耗时", "路径长度", "成功率", "稳定性", "平滑度",
        "安全得分", "扩展节点", "计算开销", "鲁棒性",
    ]
    colors = ["#2ecc71", "#3498db", "#e74c3c", "#f39c12", "#9b59b6"]

    fig = go.Figure()
    for idx, r in enumerate(ranking[:5]):
        detail = r.get("detail", {})
        values = [detail.get(k, 0) for k in keys]
        values += values[:1]
        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=labels + [labels[0]],
                name=r.get("algorithm", f"算法{idx+1}"),
                line=dict(color=colors[idx % len(colors)], width=2),
                fill="toself",
                opacity=0.3,
            )
        )

    fig.update_layout(
        title="候选算法 9 维雷达对比",
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        height=550,
        margin=dict(l=60, r=60, t=60, b=40),
    )
    return fig


def render_decision_card(decision: dict) -> None:
    """在 Streamlit 中渲染单次决策的结果卡片"""
    scene_level = decision.get("scene_level", "N/A")
    best_algorithm = decision.get("best_algorithm", "N/A")
    best_score = decision.get("best_score", 0.0)

    color = _resolve_scene_color(scene_level)
    st.markdown(f"### :{color}[{scene_level} 复杂度]")
    st.success(f"推荐算法：{best_algorithm}")
    st.metric("综合得分", f"{best_score:.4f}")


def render_reasoning_chain(decision: dict, expanded_all: bool = False) -> None:
    import json
    import streamlit as st

    env_input = st.session_state.get("env_input", {}) or {}
    features = st.session_state.get("features", None) or {}
    params = st.session_state.get("params", None)
    hypothesis = st.session_state.get("hypothesis", None)
    ranking = decision.get("ranking", [])

    status_emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}

    eval_content = []
    if ranking:
        top_detail = ranking[0].get("detail", {})
        if top_detail:
            dim_labels = [
                "耗时", "路径长度", "成功率", "稳定性", "平滑度",
                "安全得分", "扩展节点", "计算开销", "鲁棒性", "惩罚项",
            ]
            dim_keys = [
                "time_score", "length_score", "success_score", "stability_score",
                "smoothness_score", "safety_score", "expanded_nodes_score",
                "compute_cost_score", "robustness_score", "penalty",
            ]
            for label, key in zip(dim_labels, dim_keys):
                raw = top_detail.get(f"{key}_raw", top_detail.get(key, "N/A"))
                norm = top_detail.get(f"{key}_normalized", "N/A")
                weight = top_detail.get(f"{key}_weight", "N/A")
                weighted = top_detail.get(f"{key}_weighted", "N/A")
                eval_content.append((f"{label} (raw/norm/wt/wtd)", f"{raw} / {norm} / {weight} / {weighted}"))
        else:
            eval_content.append(("评分详情", "评分详情暂不可用"))
    else:
        eval_content.append(("评分详情", "评分详情暂不可用"))

    param_content = []
    if params and isinstance(params, dict):
        param_content.append(("推荐参数", params))
    else:
        param_content.append(("推荐参数", "参数暂不可用"))

    decision_content = [
        ("推荐算法", decision.get("best_algorithm", "N/A")),
        ("综合得分", f"{decision.get('best_score', 0):.4f}"),
        ("置信度", f"{decision.get('confidence', 0):.2f}"),
    ]
    if ranking:
        table_lines = ["| 排名 | 算法 | 得分 |", "|------|------|------|"]
        for i, r in enumerate(ranking[:5]):
            table_lines.append(f"| {i+1} | {r.get('algorithm', 'N/A')} | {r.get('score', 0):.4f} |")
        decision_content.append(("排名前5", "\n".join(table_lines)))
    else:
        decision_content.append(("排名前5", "暂无排名数据"))

    hyp_content = []
    if hypothesis and isinstance(hypothesis, dict) and any(hypothesis.values()):
        hyp_fields = [
            ("研究假设", "hypothesis_text"),
            ("实验计划", "experiment_plan"),
            ("预期结果", "expected_results"),
            ("边界条件", "boundary_conditions"),
        ]
        for label, key in hyp_fields:
            val = hypothesis.get(key, "")
            if val:
                hyp_content.append((label, val))
    if not hyp_content:
        hyp_content.append(("假设状态", "假设暂未生成"))

    rule_content = [("触发规则数", f"{len(decision.get('triggered_rules', []))} 条")]
    triggered = decision.get("triggered_rules", [])
    if triggered:
        for i, rule in enumerate(triggered):
            rule_content.append((f"规则{i+1}", str(rule)))
    penalty_details = decision.get("penalty_details", {})
    if penalty_details:
        for pk, pv in penalty_details.items():
            rule_content.append((f"惩罚: {pk}", str(pv)))

    agents = [
        {
            "name": "Data Agent",
            "icon": "📥",
            "status": "green",
            "content": [
                ("数据来源类型", decision.get("data_source_type", "手动输入")),
                ("地图宽度", env_input.get("map_width", "N/A")),
                ("地图高度", env_input.get("map_height", "N/A")),
                ("障碍物占比", f"{env_input.get('obstacle_ratio', 0):.2f}"),
                ("算力限制", env_input.get("compute_limit", "N/A")),
                ("优化偏好", env_input.get("optimization_preference", "平衡模式")),
            ]
        },
        {
            "name": "Map Analysis Agent",
            "icon": "🗺",
            "status": "green",
            "content": [
                ("障碍物聚类数", features.get("cluster_count", "N/A") if features else "N/A"),
                ("瓶颈通道数", features.get("bottleneck_count", "N/A") if features else "N/A"),
                ("分布熵", f"{features.get('distribution_entropy', 0):.4f}" if features else "N/A"),
                ("连通区域数", features.get("connected_region_count", "N/A") if features else "N/A"),
            ]
        },
        {
            "name": "Environment Agent",
            "icon": "🌍",
            "status": "green",
            "content": [
                ("场景等级", decision.get("scene_level", "N/A")),
                ("综合复杂度指数", f"{features.get('complexity_index', 0):.4f}" if features else "N/A"),
                ("分级依据", "obstacle_ratio阈值: <0.20=低复杂度, 0.20~0.50=中复杂度, >0.50=高复杂度"),
                ("复杂度公式", "0.45×障碍物占比 + 0.25×(1-连通性) + 0.20×拓扑随机性 + 0.10×动态变化率"),
            ]
        },
        {
            "name": "Literature Agent",
            "icon": "📚",
            "status": "yellow",
            "content": [
                ("文献事实数", f"{len(decision.get('literature_facts', []))} 条"),
                ("来源论文", decision.get("literature_sources", "暂无文献数据") if decision.get("literature_sources") else "暂无文献数据"),
            ]
        },
        {
            "name": "Knowledge Agent",
            "icon": "🧠",
            "status": "green",
            "content": [
                ("历史记录数", f"{decision.get('knowledge_record_count', 0)} 条"),
                ("覆盖场景", ", ".join(decision.get("knowledge_scenes", ["暂无历史数据"])) if decision.get("knowledge_scenes") else "暂无历史数据"),
            ]
        },
        {
            "name": "Rule Agent",
            "icon": "📏",
            "status": "green" if triggered else "yellow",
            "content": rule_content,
        },
        {
            "name": "Evaluation Agent",
            "icon": "📊",
            "status": "green" if (ranking and ranking[0].get("detail")) else "yellow",
            "content": eval_content,
        },
        {
            "name": "Parameter Agent",
            "icon": "⚙",
            "status": "green" if (params and isinstance(params, dict)) else "yellow",
            "content": param_content,
        },
        {
            "name": "Decision Agent",
            "icon": "🎯",
            "status": "green",
            "content": decision_content,
        },
        {
            "name": "Hypothesis Agent",
            "icon": "💡",
            "status": "green" if hyp_content and hyp_content[0][0] != "假设状态" else "yellow",
            "content": hyp_content,
        },
        {
            "name": "Reflection Agent",
            "icon": "🔄",
            "status": "yellow",
            "content": [
                ("假设是否支持", str(decision.get("hypothesis_supported", "N/A")) if decision.get("hypothesis_supported") is not None else "N/A"),
                ("置信度分数", f"{decision.get('confidence', 0):.2f}"),
            ]
        },
        {
            "name": "Human-Loop Agent",
            "icon": "👤",
            "status": "red" if decision.get("need_human_check") else "green",
            "content": [
                ("是否需要人工校验", "是 ⚠️" if decision.get("need_human_check") else "否"),
                ("校验原因", decision.get("human_check_reason", "无需校验") if decision.get("need_human_check") else "决策置信度充足"),
            ]
        },
    ]

    for agent in agents:
        emoji = status_emoji.get(agent["status"], "🟢")
        with st.expander(f"{emoji} {agent['icon']} {agent['name']}", expanded=expanded_all):
            for label, value in agent["content"]:
                if label == "推荐参数" and isinstance(value, dict):
                    st.markdown(f"**{label}**")
                    st.code(json.dumps(value, ensure_ascii=False, indent=2), language="json")
                elif label == "排名前5" and isinstance(value, str) and "|" in value:
                    st.markdown(f"**{label}**")
                    st.markdown(value)
                else:
                    st.markdown(f"**{label}**: {value}")


def _wrap_hypothesis_to_dict(text: str) -> dict:
    """将字符串假设包装成与 dict 假设结构一致的字典"""
    return {
        "problem_statement": "",
        "rationale": "",
        "technical_details": "",
        "datasets": "",
        "paper_title": "",
        "abstract": text,
        "methods": "",
        "experiments": "",
        "results": "",
        "references": "",
    }


def generate_markdown_report(hypothesis, decision: dict, env_input: dict) -> str:
    """根据假设与决策生成可下载的 Markdown 研究计划报告"""
    if isinstance(hypothesis, dict):
        hyp = dict(hypothesis)
    else:
        hyp = _wrap_hypothesis_to_dict(str(hypothesis))

    section_keys = [
        "problem_statement",
        "rationale",
        "technical_details",
        "datasets",
        "paper_title",
        "abstract",
        "methods",
        "experiments",
        "results",
        "references",
    ]
    section_titles = [
        "1. 待研究问题",
        "2. 解决思路",
        "3. 必要技术手段",
        "4. 数据集",
        "5. 论文标题",
        "6. 摘要",
        "7. 方法论",
        "8. 实验设计",
        "9. 实验结果",
        "10. 参考论文",
    ]

    lines = []
    lines.append("# AI Scientist 研究计划")
    lines.append("")
    lines.append("## 场景信息")
    lines.append(f"- 障碍物占比: {env_input.get('obstacle_ratio', 'N/A')}")
    lines.append(
        f"- 地图尺寸: {env_input.get('map_width', 'N/A')}×{env_input.get('map_height', 'N/A')}"
    )
    lines.append(f"- 推荐算法: {decision.get('best_algorithm', 'N/A')}")
    lines.append("")

    for title, key in zip(section_titles, section_keys):
        lines.append(f"## {title}")
        content = hyp.get(key, "")
        if not content:
            content = "*待生成*"
        lines.append(content)
        lines.append("")

    return "\n".join(lines)


def regenerate_hypothesis() -> None:
    """Streamlit 按钮回调：重新生成科学假设并写入 session_state"""
    if st.session_state.get("decision") is None:
        return

    decision = st.session_state.decision
    env_input = st.session_state.get("env_input", {}) or {}

    explanation_agent = ExplanationAgent(use_qwen=False)
    explanation = explanation_agent.explain(env_input, decision)

    hypothesis_agent = HypothesisAgent(use_qwen=False)
    new_hypothesis_text = hypothesis_agent.generate(
        env_input, decision, explanation["explanation_text"]
    )

    st.session_state.hypothesis = _wrap_hypothesis_to_dict(new_hypothesis_text)
