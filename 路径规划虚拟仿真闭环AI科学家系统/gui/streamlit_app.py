import os
import sys
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from main import PathPlanningDecisionSystem
from agents.explanation_agent import ExplanationAgent
from agents.hypothesis_agent import HypothesisAgent
from map.map_generator import MapGenerator
from map.map_parser import MapParser
from map.connectivity_checker import ConnectivityChecker
from evaluation.benchmark import BenchmarkRunner
from data.benchmark_loader import BenchmarkLoader
from gui.visualization import (
    draw_grid, draw_ranking_bar, draw_radar,
    draw_scene_indicator, draw_metric_cards,
    render_decision_card, render_reasoning_chain,
    render_enhanced_reasoning_chain,
     generate_markdown_report, regenerate_hypothesis,
    draw_10d_bar, draw_10d_radar,
    draw_multi_path_overlay, draw_animated_bar_chart,
    draw_extended_radar, highlight_pareto_front,
    export_pdf_or_fallback,
)
from gui.animation import create_search_animation
from config import DEFAULT_MAP_WIDTH, DEFAULT_MAP_HEIGHT


st.set_page_config(
    page_title="AI Scientist 路径规划算法选型系统",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def _scene_to_obstacle_range(scene_level):
    return {
        "低复杂度": (0.0, 0.20),
        "中复杂度": (0.20, 0.50),
        "高复杂度": (0.50, 1.0),
    }.get(scene_level, (0.0, 1.0))


def execute_decision_pipeline(map_width, map_height, obstacle_ratio, connectivity,
                               topology_randomness, compute_limit, random_seed,
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
        "random_seed": random_seed,
    }
    st.session_state.env_input = env_input

    gen = MapGenerator(seed=random_seed)
    grid = gen.generate(map_width, map_height, obstacle_ratio,
                         (start_x, start_y), (target_x, target_y))
    st.session_state.grid = grid
    st.session_state.start = (start_x, start_y)
    st.session_state.target = (target_x, target_y)

    checker = ConnectivityChecker()
    if not checker.is_reachable(grid, (start_x, start_y), (target_x, target_y)):
        for _ in range(5):
            grid = gen.generate(map_width, map_height, obstacle_ratio,
                                 (start_x, start_y), (target_x, target_y))
            if checker.is_reachable(grid, (start_x, start_y), (target_x, target_y)):
                break
        st.session_state.grid = grid

    benchmark = BenchmarkRunner()
    benchmark_results = benchmark.run(grid, (start_x, start_y),
                                       (target_x, target_y), n_runs=3,
                                       compute_limit=compute_limit,
                                       base_seed=random_seed)
    st.session_state.benchmark_results = benchmark_results

    system = PathPlanningDecisionSystem()
    decision = system.decide(env_input)
    st.session_state.decision = decision

    try:
        from map.map_analyzer import MapAnalyzer
        analyzer = MapAnalyzer()
        features = analyzer.analyze(grid, (start_x, start_y), (target_x, target_y),
                                     connectivity=connectivity,
                                     topology_randomness=topology_randomness,
                                     dynamic_change_rate=dynamic_change_rate)
        st.session_state.features = features
    except ImportError:
        st.session_state.features = {"scene_level": decision.get("scene_level", "unknown")}

    try:
        from agents.parameter_agent import ParameterAgent
        param_agent = ParameterAgent()
        st.session_state.params = param_agent.recommend(env_input, decision)
    except ImportError:
        st.session_state.params = None

    explanation_agent = ExplanationAgent(use_qwen=True)
    explanation = explanation_agent.explain(env_input, decision)
    hypo_agent = HypothesisAgent(use_qwen=True)
    hypothesis_text = hypo_agent.generate(env_input, decision, explanation["explanation_text"])
    from gui.visualization import _wrap_hypothesis_to_dict
    st.session_state.hypothesis = _wrap_hypothesis_to_dict(hypothesis_text)


def execute_decision_pipeline_v2(map_width, map_height, obstacle_ratio, connectivity,
                                  topology_randomness, compute_limit, random_seed,
                                  start_x, start_y, target_x, target_y,
                                  dynamic_change_rate, optimization_preference,
                                  grid_from_file=None):
    """执行一次完整的多智能体分析流水线（V2：支持文件上传和优化偏好）"""
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
        "optimization_preference": optimization_preference,
        "random_seed": random_seed,
    }
    st.session_state.env_input = env_input

    if grid_from_file is not None:
        grid = grid_from_file
        st.session_state.grid = grid
    else:
        gen = MapGenerator(seed=random_seed)
        grid = gen.generate(map_width, map_height, obstacle_ratio,
                             (start_x, start_y), (target_x, target_y))
        st.session_state.grid = grid
    st.session_state.start = (start_x, start_y)
    st.session_state.target = (target_x, target_y)

    checker = ConnectivityChecker()
    if not checker.is_reachable(grid, (start_x, start_y), (target_x, target_y)):
        if grid_from_file is not None:
            pass
        else:
            gen_fallback = MapGenerator(seed=random_seed)
            for _ in range(5):
                grid = gen_fallback.generate(map_width, map_height, obstacle_ratio,
                                              (start_x, start_y), (target_x, target_y))
                if checker.is_reachable(grid, (start_x, start_y), (target_x, target_y)):
                    break
            st.session_state.grid = grid

    benchmark = BenchmarkRunner()
    benchmark_results = benchmark.run(grid, (start_x, start_y),
                                       (target_x, target_y), n_runs=3,
                                       compute_limit=compute_limit,
                                       base_seed=random_seed)
    st.session_state.benchmark_results = benchmark_results

    system = PathPlanningDecisionSystem()
    decision = system.decide(env_input)
    st.session_state.decision = decision

    try:
        from map.map_analyzer import MapAnalyzer
        analyzer = MapAnalyzer()
        features = analyzer.analyze(grid, (start_x, start_y), (target_x, target_y),
                                     connectivity=connectivity,
                                     topology_randomness=topology_randomness,
                                     dynamic_change_rate=dynamic_change_rate)
        st.session_state.features = features
    except ImportError:
        st.session_state.features = {"scene_level": decision.get("scene_level", "unknown")}

    try:
        from agents.parameter_agent import ParameterAgent
        param_agent = ParameterAgent()
        st.session_state.params = param_agent.recommend(env_input, decision)
    except ImportError:
        st.session_state.params = None

    explanation_agent = ExplanationAgent(use_qwen=True)
    explanation = explanation_agent.explain(env_input, decision)
    hypo_agent = HypothesisAgent(use_qwen=True)
    hypothesis_text = hypo_agent.generate(env_input, decision, explanation["explanation_text"])
    from gui.visualization import _wrap_hypothesis_to_dict
    st.session_state.hypothesis = _wrap_hypothesis_to_dict(hypothesis_text)


def apply_template(preset_name):
    template_presets = {
        "低障碍(15%)": {"obstacle_ratio": 0.15, "connectivity": 0.80, "topology_randomness": 0.30},
        "中障碍(35%)": {"obstacle_ratio": 0.35, "connectivity": 0.68, "topology_randomness": 0.55},
        "高障碍(65%)": {"obstacle_ratio": 0.65, "connectivity": 0.30, "topology_randomness": 0.70},
        "迷宫型(50%)": {"obstacle_ratio": 0.50, "connectivity": 0.40, "topology_randomness": 0.80},
    }
    preset = template_presets[preset_name]
    st.session_state.obstacle_ratio_val = preset["obstacle_ratio"]
    st.session_state.connectivity_val = preset["connectivity"]
    st.session_state.topology_randomness_val = preset["topology_randomness"]
    st.session_state.uploaded_grid = None
    st.session_state.template_applied = True


def main():
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
    if "uploaded_grid" not in st.session_state:
        st.session_state.uploaded_grid = None
    if "last_uploaded_name" not in st.session_state:
        st.session_state.last_uploaded_name = None
    if "template_applied" not in st.session_state:
        st.session_state.template_applied = False
    if "all_expanded" not in st.session_state:
        st.session_state.all_expanded = False
    if "obstacle_ratio_val" not in st.session_state:
        st.session_state.obstacle_ratio_val = 0.35
    if "connectivity_val" not in st.session_state:
        st.session_state.connectivity_val = 0.68
    if "topology_randomness_val" not in st.session_state:
        st.session_state.topology_randomness_val = 0.55

    st.title("🔬 路径规划算法自适应选型多智能体 AI Scientist 系统")

    tab_map, tab_analysis, tab_reasoning, tab_report = st.tabs([
        "🗺 地图参数",
        "📊 环境分析",
        "🤖 智能体推理",
        "📄 研究报告",
    ])

    with tab_map:
        col_left, col_mid, col_right = st.columns([1, 2, 1])

        with col_left:
            st.subheader("📥 地图参数输入")

            uploaded_file = st.file_uploader(
                "📁 上传地图文件",
                type=["csv", "json", "map", "scen", "npy"],
                help="支持 CSV/JSON/.map/.scen/.npy 格式",
                key="map_file_uploader"
            )

            if uploaded_file is not None and st.session_state.get("last_uploaded_name") != uploaded_file.name:
                suffix_map = {".csv": ".csv", ".json": ".json", ".map": ".map", ".scen": ".scen", ".npy": ".npy"}
                file_suffix = suffix_map.get("." + uploaded_file.name.split(".")[-1].lower(), ".csv")
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as tmp_file:
                        tmp_file.write(uploaded_file.getbuffer())
                        tmp_path = tmp_file.name
                    parsed = MapParser().parse(tmp_path)
                    grid = parsed.get("grid")
                    if grid is not None:
                        st.session_state.uploaded_grid = grid
                        st.session_state.obstacle_ratio_val = float(grid.sum()) / max(grid.size, 1)
                        st.session_state.map_width_from_file = int(grid.shape[1])
                        st.session_state.map_height_from_file = int(grid.shape[0])
                    st.session_state.last_uploaded_name = uploaded_file.name
                except Exception as e:
                    st.error(f"地图文件解析失败: {e}")

            try:
                benchmark_maps = [""] + BenchmarkLoader().list_available_maps()
            except Exception:
                benchmark_maps = [""]
            selected_benchmark = st.selectbox(
                "📦 选择 Benchmark 地图",
                options=benchmark_maps,
                disabled=(uploaded_file is not None),
                help="选择 Moving AI benchmark 地图集"
            )

            if selected_benchmark:
                try:
                    loaded = BenchmarkLoader().load_map(selected_benchmark)
                    grid = loaded.get("grid")
                    if grid is not None:
                        st.session_state.uploaded_grid = grid
                        st.session_state.obstacle_ratio_val = float(grid.sum()) / max(grid.size, 1)
                        st.session_state.map_width_from_file = int(grid.shape[1])
                        st.session_state.map_height_from_file = int(grid.shape[0])
                except Exception as e:
                    st.error(f"Benchmark 地图加载失败: {e} (请检查网络连接)")

            st.caption("🎨 随机地图模板")
            tmpl_cols = st.columns(4)
            template_presets = {
                "低障碍(15%)": {"obstacle_ratio": 0.15, "connectivity": 0.80, "topology_randomness": 0.30},
                "中障碍(35%)": {"obstacle_ratio": 0.35, "connectivity": 0.68, "topology_randomness": 0.55},
                "高障碍(65%)": {"obstacle_ratio": 0.65, "connectivity": 0.30, "topology_randomness": 0.70},
                "迷宫型(50%)": {"obstacle_ratio": 0.50, "connectivity": 0.40, "topology_randomness": 0.80},
            }
            for idx, (name, preset) in enumerate(template_presets.items()):
                with tmpl_cols[idx]:
                    st.button(name, key=f"tmpl_{idx}", use_container_width=True,
                              on_click=apply_template, args=(name,))

            map_width = st.slider("地图宽度", 10, 500, st.session_state.get("map_width_from_file", DEFAULT_MAP_WIDTH), 10)
            map_height = st.slider("地图高度", 10, 500, st.session_state.get("map_height_from_file", DEFAULT_MAP_HEIGHT), 10)
            obstacle_ratio = st.slider("障碍物占比", 0.0, 1.0, st.session_state.obstacle_ratio_val, 0.01, help="地图中障碍物所占比例，0~1")
            connectivity = st.slider("通道连通性", 0.0, 1.0, st.session_state.connectivity_val, 0.01, help="越高表示连通区域越多")
            topology_randomness = st.slider("拓扑随机性", 0.0, 1.0, st.session_state.topology_randomness_val, 0.01, help="越高表示障碍分布越随机")
            compute_limit = st.radio("算力限制", ["low", "medium", "high"], index=1, horizontal=True,
                                     help="low=边缘设备（算力受限）/ medium=标准桌面 / high=服务器集群（算力充足）")

            optimization_preference = st.radio(
                "🎯 优化偏好",
                ["耗时优先", "成功率优先", "路径最短", "平衡模式"],
                index=3,
                horizontal=True,
                help="影响算法评分权重的偏好方向"
            )

            with st.expander("⚙ 高级参数"):
                start_x = st.number_input("起点 X", 0, map_width - 1, 0)
                start_y = st.number_input("起点 Y", 0, map_height - 1, 0)
                target_x = st.number_input("终点 X", 0, map_width - 1, map_width - 1)
                target_y = st.number_input("终点 Y", 0, map_height - 1, map_height - 1)
                dynamic_change_rate = st.slider("动态变化率", 0.0, 1.0, 0.0, 0.01, help="非零时模拟动态障碍物环境")
                random_seed = st.number_input("随机种子", 0, 9999, 42)

            run_btn = st.button("▶ 开始多智能体分析", type="primary", use_container_width=True)
            regenerate_btn = st.button("🔄 重新生成地图", use_container_width=True)

        with col_mid:
            st.subheader("🗺 地图预览")
            if regenerate_btn:
                st.session_state.uploaded_grid = None

            if run_btn or regenerate_btn:
                if st.session_state.uploaded_grid is not None:
                    grid = st.session_state.uploaded_grid
                    st.session_state.grid = grid
                else:
                    generator = MapGenerator(seed=random_seed)
                    grid = generator.generate(map_width, map_height, obstacle_ratio,
                                               (start_x, start_y), (target_x, target_y))
                    st.session_state.grid = grid
                st.session_state.start = (start_x, start_y)
                st.session_state.target = (target_x, target_y)

            if run_btn:
                with st.spinner("🧠 多智能体系统正在分析..."):
                    if st.session_state.uploaded_grid is not None:
                        execute_decision_pipeline_v2(
                            map_width, map_height, obstacle_ratio, connectivity,
                            topology_randomness, compute_limit, random_seed,
                            start_x, start_y, target_x, target_y,
                            dynamic_change_rate, optimization_preference,
                            grid_from_file=st.session_state.uploaded_grid,
                        )
                    else:
                        execute_decision_pipeline_v2(
                            map_width, map_height, obstacle_ratio, connectivity,
                            topology_randomness, compute_limit, random_seed,
                            start_x, start_y, target_x, target_y,
                            dynamic_change_rate, optimization_preference,
                            grid_from_file=None,
                        )
                st.success("✅ 分析完成！")
                st.rerun()

            if st.session_state.grid is not None:
                show_multi_path = st.checkbox("🛤 显示所有算法路径", value=False, key="show_multi_path",
                                              help="勾选后在地图上叠加 5 种算法的最优路径")
                if show_multi_path and st.session_state.benchmark_results is not None:
                    try:
                        from algorithms.astar import AStar
                        from algorithms.aco import AntColony
                        from algorithms.pso import ParticleSwarm
                        from algorithms.sa import SimulatedAnnealing
                        from algorithms.hybrid import HybridAlgorithm
                        from config import RUNTIME_BUDGET_S
                        overlay_budget = RUNTIME_BUDGET_S.get(compute_limit, 0.5)
                        algo_classes = {
                            "A*": AStar(time_budget_s=overlay_budget),
                            "ACO": AntColony(seed=random_seed, time_budget_s=overlay_budget),
                            "PSO": ParticleSwarm(seed=random_seed, time_budget_s=overlay_budget),
                            "SA": SimulatedAnnealing(seed=random_seed, time_budget_s=overlay_budget),
                            "混合优化算法": HybridAlgorithm(time_budget_s=overlay_budget),
                        }
                        paths = {}
                        sx, sy = st.session_state.start
                        tx, ty = st.session_state.target
                        for name, algo in algo_classes.items():
                            try:
                                res = algo.search(st.session_state.grid, (sx, sy), (tx, ty))
                                if res.get("success", False) and res.get("path"):
                                    paths[name] = res["path"]
                            except Exception:
                                continue
                        if paths:
                            fig_grid = draw_multi_path_overlay(
                                st.session_state.grid, paths,
                                start=st.session_state.start,
                                target=st.session_state.target,
                            )
                        else:
                            fig_grid = draw_grid(
                                st.session_state.grid,
                                start=st.session_state.start,
                                target=st.session_state.target,
                                title=f"栅格地图预览 (障碍物占比={obstacle_ratio:.0%})"
                            )
                    except Exception as e:
                        st.warning(f"多路径叠加渲染失败：{e}")
                        fig_grid = draw_grid(
                            st.session_state.grid,
                            start=st.session_state.start,
                            target=st.session_state.target,
                            title=f"栅格地图预览 (障碍物占比={obstacle_ratio:.0%})"
                        )
                else:
                    fig_grid = draw_grid(
                        st.session_state.grid,
                        start=st.session_state.start,
                        target=st.session_state.target,
                        title=f"栅格地图预览 (障碍物占比={obstacle_ratio:.0%})"
                    )
                st.plotly_chart(fig_grid, use_container_width=True,
                                key="chart_grid_main")

                if (st.session_state.decision is not None
                        and st.session_state.decision.get("best_algorithm") == "A*"
                        and st.session_state.benchmark_results is not None):
                    if st.button("▶ 播放 A* 搜索过程动画", key="btn_play_astar", use_container_width=True):
                        try:
                            fig_anim = create_search_animation(
                                st.session_state.grid, "A*",
                                st.session_state.start, st.session_state.target,
                            )
                            st.plotly_chart(fig_anim, use_container_width=True,
                                            key="chart_astar_anim")
                        except Exception as e:
                            st.warning(f"A* 动画渲染失败：{e}")
            elif st.session_state.uploaded_grid is not None:
                fig_grid = draw_grid(
                    st.session_state.uploaded_grid,
                    start=st.session_state.start,
                    target=st.session_state.target,
                    title="上传地图预览"
                )
                st.plotly_chart(fig_grid, use_container_width=True,
                                key="chart_grid_uploaded")
            else:
                st.info("点击「开始多智能体分析」或上传地图文件生成预览")

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

    with tab_analysis:
        if st.session_state.decision is not None:
            col_left, col_right = st.columns([1, 1])

            with col_left:
                st.subheader("📊 场景分析")
                decision = st.session_state.decision

                scene_level = decision.get("scene_level", "N/A")
                level_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴",
                               "低复杂度": "🟢", "中复杂度": "🟡", "高复杂度": "🔴"}
                st.metric("场景等级", f"{level_emoji.get(scene_level, '⚪')} {scene_level}")

                if st.session_state.features:
                    features = st.session_state.features
                    st.metric("综合复杂度指数", f"{features.get('complexity_index', 0):.3f}")

                    fcol1, fcol2, fcol3 = st.columns(3)
                    with fcol1:
                        st.metric("障碍物聚类数", features.get("cluster_count", "N/A"))
                    with fcol2:
                        st.metric("瓶颈通道数", features.get("bottleneck_count", "N/A"))
                    with fcol3:
                        st.metric("分布熵", f"{features.get('distribution_entropy', features.get('entropy', 0)):.3f}")

                st.info(f"**推荐算法：{decision['best_algorithm']}**")
                st.metric("综合得分", f"{decision['best_score']:.4f}")

            with col_right:
                st.subheader("📈 算法综合评分排名（点击下拉切换指标）")
                fig_bar = draw_animated_bar_chart(decision["ranking"])
                st.plotly_chart(fig_bar, use_container_width=True, key="chart_animated_bar")

            st.divider()

            st.subheader("📊 推荐算法 10 维指标评分")
            top_detail = decision["ranking"][0].get("detail", {}) if decision.get("ranking") else {}
            fig_10d_bar = draw_10d_bar(top_detail)
            st.plotly_chart(fig_10d_bar, key="chart_10d_bar", use_container_width=True)

            st.subheader("🎯 五算法 10 维雷达对比")
            fig_10d_radar = draw_10d_radar(decision["ranking"])
            st.plotly_chart(fig_10d_radar, key="chart_10d_radar", use_container_width=True)

            if st.session_state.benchmark_results:
                st.subheader("📋 Benchmark 实际运行结果对比")
                import pandas as pd
                table_data = []
                for r in st.session_state.benchmark_results:
                    table_data.append({
                        "算法": r.get("algorithm", "N/A"),
                        "平均耗时(s)": f"{r.get('avg_time', 0):.4f}",
                        "平均路径长度": f"{r.get('avg_path_length', 0):.2f}",
                        "成功率": f"{r.get('success_rate', 0):.2%}",
                        "稳定性": f"{r.get('stability_score', 0):.4f}",
                        "平滑度": f"{r.get('smoothness', 0):.4f}",
                        "安全得分": f"{r.get('safety_score', 0):.4f}",
                        "扩展节点数": r.get("expanded_nodes", "N/A"),
                        "计算开销": f"{r.get('compute_cost', 0):.4f}",
                        "鲁棒性": f"{r.get('robustness', 0):.4f}",
                    })
                df = pd.DataFrame(table_data)
                st.dataframe(df, use_container_width=True, hide_index=True)

            knowledge_records = decision.get("knowledge_records", []) or decision.get("algorithm_records", [])
            if knowledge_records and st.session_state.benchmark_results:
                hist_success = sum(r.get("success_rate", 0) for r in knowledge_records) / max(len(knowledge_records), 1)
                bench_success_avg = sum(r.get("success_rate", 0) for r in st.session_state.benchmark_results) / max(len(st.session_state.benchmark_results), 1)
                if hist_success > 0:
                    deviation = abs(bench_success_avg - hist_success) / hist_success
                    if deviation > 0.20:
                        st.warning(f"⚠️ 当前成功率({bench_success_avg:.2%})与历史均值({hist_success:.2%})偏差 {deviation:.1%}，超过 20% 阈值")

            col_bottom_left, col_bottom_right = st.columns([1, 1])

            with col_bottom_left:
                st.subheader("🎯 多指标雷达图")
                radar_dim = st.radio("雷达维度", ["4 维", "10 维"],
                                      horizontal=True, key="radar_dim",
                                      label_visibility="collapsed")
                if radar_dim == "10 维":
                    fig_radar = draw_extended_radar(decision["ranking"])
                else:
                    fig_radar = draw_radar(decision["ranking"])
                st.plotly_chart(fig_radar, use_container_width=True, key="chart_radar_dim")

                st.subheader("🟥 Pareto 前沿（耗时 vs 路径长度）")
                fig_pareto = highlight_pareto_front(decision["ranking"])
                st.plotly_chart(fig_pareto, use_container_width=True, key="chart_pareto")

            with col_bottom_right:
                st.subheader("📋 算法对比数据表")
                if st.session_state.benchmark_results:
                    benchmark = BenchmarkRunner()
                    benchmark.print_table(st.session_state.benchmark_results)
        else:
            st.info("请先在「地图参数」标签页中执行分析。")

    with tab_reasoning:
        if st.session_state.decision is not None:
            decision = st.session_state.decision
            col_left, col_right = st.columns([1, 1])

            with col_left:
                st.subheader("🏆 算法选型结果")
                render_decision_card(decision)

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

                st.divider()
                st.subheader("💬 DeepSeek 解释")
                env_input = st.session_state.env_input
                explanation_agent = ExplanationAgent(use_qwen=True)
                explanation = explanation_agent.explain(env_input, decision)
                st.info(explanation["explanation_text"])

            with col_right:
                if "all_expanded" not in st.session_state:
                    st.session_state.all_expanded = False

                st.subheader("🧠 多智能体推理链（增强版：含置信度与 I/O 详情）")
                render_enhanced_reasoning_chain(decision)

                st.divider()
                st.subheader("⚙ 推荐算法参数")
                if st.session_state.params:
                    import json
                    st.code(json.dumps(st.session_state.params, ensure_ascii=False, indent=2), language="json")
        else:
            st.info("请先在「地图参数」标签页中执行分析。")

    with tab_report:
        if st.session_state.hypothesis is not None:
            hypothesis = st.session_state.hypothesis
            decision = st.session_state.decision
            env_input = st.session_state.env_input

            need_human = False
            if decision:
                ranking = decision.get("ranking", [])
                if decision.get("need_human_check"):
                    need_human = True
                elif len(ranking) >= 2:
                    score_diff = abs(ranking[0].get("score", 0) - ranking[1].get("score", 0))
                    if score_diff < 0.05:
                        need_human = True

            if need_human:
                st.error("⚠️ AI 决策存在不确定性，请人工审核")
                with st.expander("👤 人在回路 - 人工校验面板", expanded=True):
                    pref_options = ["耗时优先", "成功率优先", "路径最短", "平衡模式"]
                    current_pref = env_input.get("optimization_preference", "平衡模式")
                    default_idx = pref_options.index(current_pref) if current_pref in pref_options else 3
                    new_preference = st.selectbox(
                        "调整优化优先级",
                        pref_options,
                        index=default_idx,
                        key="human_loop_preference"
                    )
                    feedback = st.text_area("质疑结论（输入您的反馈意见）", placeholder="例如：我认为在当前场景下应该优先考虑成功率...", key="human_loop_feedback")
                    if st.button("🔄 提交反馈并重新分析", type="primary", use_container_width=True):
                        st.session_state.env_input["human_feedback"] = feedback
                        st.session_state.env_input["optimization_preference"] = new_preference
                        with st.spinner("🔄 正在基于您的反馈重新分析..."):
                            mw = env_input.get("map_width", DEFAULT_MAP_WIDTH)
                            mh = env_input.get("map_height", DEFAULT_MAP_HEIGHT)
                            sp = env_input.get("start_point", [0, 0])
                            tp = env_input.get("target_point", [mw - 1, mh - 1])
                            execute_decision_pipeline_v2(
                                mw, mh,
                                env_input.get("obstacle_ratio", 0.35),
                                env_input.get("connectivity", 0.68),
                                env_input.get("topology_randomness", 0.55),
                                env_input.get("compute_limit", "medium"),
                                env_input.get("random_seed", 42),
                                sp[0], sp[1],
                                tp[0] if isinstance(tp, list) else mw - 1,
                                tp[1] if isinstance(tp, list) else mh - 1,
                                env_input.get("dynamic_change_rate", 0.0),
                                new_preference,
                                grid_from_file=st.session_state.get("uploaded_grid"),
                            )
                        st.rerun()

            st.subheader("📄 科学假设与研究计划")

            sections = [
                ("### 1. 待研究问题 (Problem Statement)", hypothesis.get("problem_statement", "")),
                ("### 2. 解决思路 (Rationale)", hypothesis.get("rationale", "")),
                ("### 3. 必要技术手段 (Technical Details)", hypothesis.get("technical_details", "")),
                ("### 4. 数据集 (Datasets)", hypothesis.get("datasets", "")),
                ("### 5. 论文标题 (Paper Title)", hypothesis.get("paper_title", "")),
                ("### 6. 摘要 (Paper Abstract)", hypothesis.get("abstract", "")),
                ("### 7. 方法论 (Methods)", hypothesis.get("methods", "")),
                ("### 8. 实验设计 (Experiments)", hypothesis.get("experiments", "")),
                ("### 9. 实验结果 (Results)", hypothesis.get("results", "")),
                ("### 10. 参考论文 (References)", hypothesis.get("references", "")),
            ]

            for i, (title, content) in enumerate(sections):
                st.markdown(title)
                if title.startswith("### 9. 实验结果") and st.session_state.benchmark_results:
                    import plotly.graph_objects as go
                    algo_names = [r["algorithm"] for r in st.session_state.benchmark_results]
                    success_rates = [r.get("success_rate", 0) for r in st.session_state.benchmark_results]
                    fig_bar_success = go.Figure(go.Bar(x=algo_names, y=success_rates, text=[f"{v:.1%}" for v in success_rates], textposition="auto"))
                    fig_bar_success.update_layout(title="各算法成功率对比", yaxis_tickformat=".0%")
                    st.plotly_chart(fig_bar_success, key="chart_bar_success", use_container_width=True)

                    if decision.get("ranking"):
                        fig_radar = draw_10d_radar(decision["ranking"])
                        st.plotly_chart(fig_radar, key="chart_radar_report", use_container_width=True)
                if title.startswith("### 10. 参考论文"):
                    import re
                    content_processed = content
                    for match in re.finditer(r"(https?://[^\s]+)", content):
                        url = match.group(0)
                        content_processed = content_processed.replace(url, f"[{url}]({url})")
                    for match in re.finditer(r"doi[:\s]*([^\s]+)", content):
                        doi = match.group(1)
                        content_processed = content_processed.replace(match.group(0), f"[DOI: {doi}](https://doi.org/{doi})")
                    st.markdown(content_processed if content_processed else "*待生成*")
                else:
                    st.markdown(content if content else "*待生成*")
                st.divider()

            st.subheader("📥 导出报告")
            exp_col1, exp_col2, exp_col3, exp_col4 = st.columns(4)

            with exp_col1:
                full_report = generate_markdown_report(hypothesis, decision, env_input)
                st.download_button(
                    "📥 导出 Markdown 报告",
                    data=full_report,
                    file_name="ai_scientist_research_report.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

            with exp_col2:
                import json as json_mod, io
                export_data = {
                    "decision": {k: v for k, v in decision.items() if k != "ranking_detail_raw"},
                    "hypothesis": hypothesis,
                    "env_input": env_input,
                }
                if st.session_state.benchmark_results:
                    bench_export = []
                    for r in st.session_state.benchmark_results:
                        br = {}
                        for k, v in r.items():
                            if isinstance(v, (str, int, float, bool, type(None))):
                                br[k] = v
                            elif isinstance(v, (list, dict)):
                                br[k] = v
                            else:
                                br[k] = str(v)
                        bench_export.append(br)
                    export_data["benchmark_results"] = bench_export
                json_str = json_mod.dumps(export_data, ensure_ascii=False, indent=2, default=str)
                st.download_button(
                    "📥 导出 JSON 数据",
                    data=json_str,
                    file_name="ai_scientist_data.json",
                    mime="application/json",
                    use_container_width=True,
                )

            with exp_col3:
                try:
                    from data.experiment_db import ExperimentDB
                    import pandas as pd, io as csv_io
                    db = ExperimentDB()
                    scene_level = decision.get("scene_level", "")
                    if scene_level:
                        min_o, max_o = _scene_to_obstacle_range(scene_level)
                        records = db.query_runs_by_scene(min_o, max_o)
                    else:
                        records = []
                    if records:
                        csv_buffer = csv_io.StringIO()
                        df_csv = pd.DataFrame(records)
                        df_csv.to_csv(csv_buffer, index=False)
                        st.download_button(
                            "📥 导出实验数据 CSV",
                            data=csv_buffer.getvalue(),
                            file_name="ai_scientist_experiments.csv",
                            mime="text/csv",
                            use_container_width=True,
                        )
                    else:
                        st.button("📥 导出实验数据 CSV", disabled=True, help="暂无实验记录", use_container_width=True)
                except Exception:
                    st.button("📥 导出实验数据 CSV", disabled=True, help="数据库不可用", use_container_width=True)

            with exp_col4:
                full_report_md = generate_markdown_report(hypothesis, decision, env_input)
                pdf_data, pdf_mime, pdf_fallback = export_pdf_or_fallback(
                    full_report_md, "ai_scientist_research_report.pdf"
                )
                if pdf_fallback:
                    st.caption("⚠️ pdfkit/wkhtmltopdf 未安装，已降级为 Markdown")
                st.download_button(
                    "📥 导出 PDF 报告",
                    data=pdf_data,
                    file_name="ai_scientist_research_report.pdf" if not pdf_fallback else "ai_scientist_research_report.md",
                    mime=pdf_mime,
                    use_container_width=True,
                )
        else:
            st.info("请先在「地图参数」标签页中执行分析，再查看研究报告。")


if __name__ == "__main__":
    main()
