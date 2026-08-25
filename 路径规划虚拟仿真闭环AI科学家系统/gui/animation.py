# gui/animation.py — 路径搜索过程动画（Phase 1.1）

import plotly.graph_objects as go
import numpy as np

from algorithms.astar import AStar


def _build_frame_data(grid, start, target, visited, frontier, path):
    """构建单帧的完整 trace 列表（背景 + 起点 + 终点 + 动态层）。"""
    data = []

    background = go.Heatmap(
        z=grid,
        colorscale=[[0, "white"], [1, "black"]],
        showscale=False,
        hoverinfo="skip",
        zmin=0,
        zmax=1,
    )
    data.append(background)

    data.append(go.Scatter(
        x=[start[0]],
        y=[start[1]],
        mode="markers",
        marker=dict(symbol="star", size=15, color="green"),
        name="起点",
        hovertemplate="起点 (%{x},%{y})<extra></extra>",
    ))

    data.append(go.Scatter(
        x=[target[0]],
        y=[target[1]],
        mode="markers",
        marker=dict(symbol="star", size=15, color="red"),
        name="终点",
        hovertemplate="终点 (%{x},%{y})<extra></extra>",
    ))

    if len(visited) > 0:
        vx = [p[0] for p in visited]
        vy = [p[1] for p in visited]
        data.append(go.Scatter(
            x=vx,
            y=vy,
            mode="markers",
            marker=dict(size=6, color="lightblue", symbol="square"),
            name="已访问",
            hovertemplate="已访问 (%{x},%{y})<extra></extra>",
        ))

    if len(frontier) > 0:
        fx = [p[0] for p in frontier]
        fy = [p[1] for p in frontier]
        data.append(go.Scatter(
            x=fx,
            y=fy,
            mode="markers",
            marker=dict(size=6, color="orange", symbol="circle"),
            name="边界",
            hovertemplate="边界 (%{x},%{y})<extra></extra>",
        ))

    if path is not None and len(path) > 1:
        px = [p[0] for p in path]
        py = [p[1] for p in path]
        data.append(go.Scatter(
            x=px,
            y=py,
            mode="lines+markers",
            line=dict(color="blue", width=2),
            name="当前路径",
            hovertemplate="路径 (%{x},%{y})<extra></extra>",
        ))

    return data


def create_search_animation(grid, algorithm: str, start, target) -> go.Figure:
    """创建路径搜索过程的 Plotly 动画。

    Args:
        grid: numpy 数组，0=可通行, 1=障碍物
        algorithm: "A*" / "astar" / "ACO" / "aco" / "PSO" / "pso" / "SA" / "sa" / "混合优化算法" 等
        start: 起点 tuple
        target: 终点 tuple

    Returns:
        plotly.graph_objects.Figure，包含 Frames 动画
    """
    algo_key = (algorithm or "").strip().lower()
    algo_key = algo_key.replace("*", "").replace(" ", "")

    if algo_key not in {"a", "astar", "a_star", "a-star"}:
        fig = go.Figure()
        fig.update_layout(
            title=f"{algorithm} 路径搜索动画暂未实现",
            annotations=[dict(
                text="该算法的搜索过程动画将在后续 Phase 2 / Phase 3 中实现。\n当前仅 A* 支持逐步动画。",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=14),
            )],
            height=400,
        )
        return fig

    astar = AStar()
    result = astar.search_with_steps(grid, start, target)
    steps = result.get("frames", [])

    if not steps:
        fig = go.Figure()
        fig.update_layout(
            title=f"{algorithm} 搜索过程动画（无帧数据）",
            height=400,
        )
        return fig

    initial_data = _build_frame_data(
        grid,
        start,
        target,
        steps[0].get("visited", set()),
        steps[0].get("frontier", set()),
        steps[0].get("path", []),
    )

    plotly_frames = [
        go.Frame(
            data=_build_frame_data(
                grid,
                start,
                target,
                frame_data.get("visited", set()),
                frame_data.get("frontier", set()),
                frame_data.get("path", []),
            ),
            name=f"frame_{i}",
        )
        for i, frame_data in enumerate(steps)
    ]

    fig = go.Figure(data=initial_data, frames=plotly_frames)

    fig.update_layout(
        title=f"{algorithm} 搜索过程动画（共 {len(plotly_frames)} 帧）",
        xaxis=dict(scaleanchor="y", scaleratio=1, showgrid=False),
        yaxis=dict(autorange="reversed", showgrid=False),
        updatemenus=[dict(
            type="buttons",
            buttons=[
                dict(
                    label="▶ 播放",
                    method="animate",
                    args=[None, {"frame": {"duration": 200, "redraw": True}, "fromcurrent": True}],
                ),
                dict(
                    label="⏸ 暂停",
                    method="animate",
                    args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}],
                ),
            ],
            direction="left",
            pad={"r": 10, "t": 10},
            showactive=False,
            x=0.1,
            xanchor="right",
            y=0,
            yanchor="top",
        )],
        sliders=[dict(
            steps=[dict(
                args=[[f"frame_{i}"], {"frame": {"duration": 200, "redraw": True}, "mode": "immediate"}],
                label=str(i + 1),
                method="animate",
            ) for i in range(len(plotly_frames))],
            active=0,
            transition={"duration": 0},
            x=0.1,
            len=0.9,
            xanchor="left",
        )],
        height=500,
        margin=dict(l=10, r=10, t=50, b=10),
    )

    return fig
