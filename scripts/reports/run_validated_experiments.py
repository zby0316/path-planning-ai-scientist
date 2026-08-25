from __future__ import annotations

import json
import math
import random
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.ndimage import distance_transform_edt


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "路径规划虚拟仿真闭环AI科学家系统"
DATA_DIR = ROOT / "evidence" / "validated_experiments"
FIG_DIR = ROOT / "assets" / "reports" / "figures"
sys.path.insert(0, str(PROJECT))

from algorithms.aco import AntColony
from algorithms.astar import AStar
from algorithms.hybrid import HybridAlgorithm
from algorithms.pso import ParticleSwarm
from algorithms.sa import SimulatedAnnealing


ALGORITHM_ORDER = ["A*", "ACO", "PSO", "SA", "混合优化算法"]
ALGORITHM_LABELS = {
    "A*": "A*",
    "ACO": "ACO",
    "PSO": "PSO",
    "SA": "SA",
    "混合优化算法": "Hybrid",
}
COLORS = {
    "A*": "#1f77b4",
    "ACO": "#ff7f0e",
    "PSO": "#2ca02c",
    "SA": "#d62728",
    "混合优化算法": "#9467bd",
}


@dataclass
class RunRecord:
    experiment: str
    obstacle_target: float
    obstacle_actual: float
    width: int
    height: int
    map_index: int
    frame_index: int
    dynamic_rate: float
    algorithm: str
    repeat: int
    seed: int
    runtime_s: float
    reported_success: int
    valid_success: int
    geometric_length: float | None
    turning_points: int
    safety_score: float
    nodes_expanded: int
    path_nodes: int
    invalid_reason: str


def configure_fonts() -> None:
    plt.rcParams["font.sans-serif"] = [
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False


def make_algorithm(name: str):
    if name == "A*":
        return AStar().search
    if name == "ACO":
        algo = AntColony()
        algo.n_ants = 10
        algo.n_iterations = 20
        return algo.search
    if name == "PSO":
        return ParticleSwarm(n_particles=10, n_iterations=20).search
    if name == "SA":
        algo = SimulatedAnnealing()
        algo.initial_temp = 100.0
        algo.cooling_rate = 0.9
        algo.min_temp = 0.01
        algo.max_iter_per_temp = 10
        return algo.search
    if name == "混合优化算法":
        return HybridAlgorithm().search
    raise KeyError(name)


def build_monotone_corridor(width: int, height: int, rng: np.random.Generator) -> list[tuple[int, int]]:
    x, y = 0, 0
    corridor = [(x, y)]
    while x < width - 1 or y < height - 1:
        if x == width - 1:
            y += 1
        elif y == height - 1:
            x += 1
        elif rng.random() < 0.5:
            x += 1
        else:
            y += 1
        corridor.append((x, y))
    return corridor


def generate_connected_grid(width: int, height: int, obstacle_ratio: float, seed: int):
    rng = np.random.default_rng(seed)
    corridor = build_monotone_corridor(width, height, rng)
    reserved = {y * width + x for x, y in corridor}
    all_indices = np.arange(width * height)
    available = np.array([idx for idx in all_indices if int(idx) not in reserved], dtype=int)
    obstacle_count = min(int(round(width * height * obstacle_ratio)), len(available))
    chosen = rng.choice(available, size=obstacle_count, replace=False)
    grid = np.zeros((height, width), dtype=np.int8)
    grid.flat[chosen] = 1
    return grid, corridor


def dynamic_sequence(
    base_grid: np.ndarray,
    corridor: list[tuple[int, int]],
    rate: float,
    steps: int,
    seed: int,
) -> list[np.ndarray]:
    rng = np.random.default_rng(seed)
    frames = [base_grid.copy()]
    current = base_grid.copy()
    reserved = {(x, y) for x, y in corridor}
    h, w = current.shape
    for _ in range(1, steps):
        free = [(x, y) for y in range(h) for x in range(w) if current[y, x] == 0 and (x, y) not in reserved]
        blocked = [(x, y) for y in range(h) for x in range(w) if current[y, x] == 1 and (x, y) not in reserved]
        swaps = max(1, int(round((h * w - len(reserved)) * rate / 2)))
        swaps = min(swaps, len(free), len(blocked))
        if swaps:
            free_idx = rng.choice(len(free), size=swaps, replace=False)
            blocked_idx = rng.choice(len(blocked), size=swaps, replace=False)
            for idx in free_idx:
                x, y = free[int(idx)]
                current[y, x] = 1
            for idx in blocked_idx:
                x, y = blocked[int(idx)]
                current[y, x] = 0
        frames.append(current.copy())
    return frames


def bresenham_cells(a: tuple[int, int], b: tuple[int, int]) -> list[tuple[int, int]]:
    x0, y0 = a
    x1, y1 = b
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    cells = [(x0, y0)]
    while (x0, y0) != (x1, y1):
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
        cells.append((x0, y0))
    return cells


def validate_path(
    grid: np.ndarray,
    path: list,
    start: tuple[int, int],
    target: tuple[int, int],
    allow_line_segments: bool,
):
    if not path:
        return False, "empty_path", []
    points = [tuple(int(v) for v in p) for p in path]
    if points[0] != start:
        return False, "wrong_start", []
    if points[-1] != target:
        return False, "wrong_target", []
    h, w = grid.shape
    expanded = [points[0]]
    for a, b in zip(points[:-1], points[1:]):
        if not allow_line_segments and abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1:
            return False, "non_adjacent_segment", []
        cells = bresenham_cells(a, b)
        for x, y in cells:
            if not (0 <= x < w and 0 <= y < h):
                return False, "out_of_bounds", []
            if grid[y, x] == 1:
                return False, "collision", []
        expanded.extend(cells[1:])
    return True, "", expanded


def geometric_length(path: list[tuple[int, int]]) -> float:
    return float(
        sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path[:-1], path[1:]))
    )


def count_turns(path: list[tuple[int, int]]) -> int:
    if len(path) < 3:
        return 0
    turns = 0
    prev = None
    for a, b in zip(path[:-1], path[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        norm = math.hypot(dx, dy) or 1.0
        direction = (round(dx / norm, 6), round(dy / norm, 6))
        if prev is not None and direction != prev:
            turns += 1
        prev = direction
    return turns


def safety_score(grid: np.ndarray, expanded_path: list[tuple[int, int]]) -> float:
    if not expanded_path:
        return 0.0
    distance = distance_transform_edt(grid == 0)
    values = [float(distance[y, x]) for x, y in expanded_path]
    return float(np.mean(values) / max(grid.shape))


def run_one(
    experiment: str,
    grid: np.ndarray,
    obstacle_target: float,
    map_index: int,
    frame_index: int,
    dynamic_rate: float,
    algorithm: str,
    repeat: int,
    seed: int,
):
    np.random.seed(seed)
    random.seed(seed)
    start = (0, 0)
    target = (grid.shape[1] - 1, grid.shape[0] - 1)
    func = make_algorithm(algorithm)
    t0 = time.perf_counter()
    try:
        result = func(grid.copy(), start, target)
        error = ""
    except Exception as exc:
        result = {"success": False, "path": []}
        error = f"exception:{type(exc).__name__}"
    runtime = time.perf_counter() - t0
    path = result.get("path", []) or []
    reported = bool(result.get("success", False))
    valid, reason, expanded = validate_path(
        grid,
        path,
        start,
        target,
        allow_line_segments=(algorithm == "混合优化算法"),
    )
    valid_success = bool(reported and valid)
    invalid_reason = error or (reason if not valid else "")
    return RunRecord(
        experiment=experiment,
        obstacle_target=float(obstacle_target),
        obstacle_actual=float(np.mean(grid == 1)),
        width=int(grid.shape[1]),
        height=int(grid.shape[0]),
        map_index=int(map_index),
        frame_index=int(frame_index),
        dynamic_rate=float(dynamic_rate),
        algorithm=algorithm,
        repeat=int(repeat),
        seed=int(seed),
        runtime_s=float(runtime),
        reported_success=int(reported),
        valid_success=int(valid_success),
        geometric_length=geometric_length(path) if valid_success else None,
        turning_points=count_turns(path) if valid_success else 0,
        safety_score=safety_score(grid, expanded) if valid_success else 0.0,
        nodes_expanded=int(result.get("nodes_expanded", 0) or 0),
        path_nodes=len(path),
        invalid_reason=invalid_reason,
    ), path


def static_experiments():
    records: list[RunRecord] = []
    map_bank = {}
    representative = {}
    ratios = [0.15, 0.35, 0.55]
    scales = [(30, 30), (50, 50)]
    for ratio_index, ratio in enumerate(ratios):
        for scale_index, (width, height) in enumerate(scales):
            for map_index in range(10):
                map_seed = 2026071100 + ratio_index * 10000 + scale_index * 1000 + map_index
                grid, corridor = generate_connected_grid(width, height, ratio, map_seed)
                map_bank[(ratio, width, map_index)] = (grid, corridor)
                for algorithm_index, algorithm in enumerate(ALGORITHM_ORDER):
                    for repeat in range(3):
                        run_seed = map_seed + algorithm_index * 100 + repeat
                        rec, path = run_one(
                            "static",
                            grid,
                            ratio,
                            map_index,
                            0,
                            0.0,
                            algorithm,
                            repeat,
                            run_seed,
                        )
                        records.append(rec)
                        if ratio == 0.35 and width == 30 and map_index == 0 and repeat == 0:
                            representative[algorithm] = path
    return records, map_bank, representative


def dynamic_experiments():
    records: list[RunRecord] = []
    sample_frames = {}
    for rate_index, rate in enumerate([0.03, 0.08]):
        for ratio_index, ratio in enumerate([0.35, 0.55]):
            for map_index in range(5):
                map_seed = 2026075000 + rate_index * 10000 + ratio_index * 1000 + map_index
                grid, corridor = generate_connected_grid(30, 30, ratio, map_seed)
                frames = dynamic_sequence(grid, corridor, rate, 5, map_seed + 77)
                if map_index == 0:
                    sample_frames[(rate, ratio)] = frames
                for frame_index, frame in enumerate(frames):
                    for algorithm_index, algorithm in enumerate(ALGORITHM_ORDER):
                        run_seed = map_seed + frame_index * 500 + algorithm_index * 100
                        rec, _ = run_one(
                            "dynamic",
                            frame,
                            ratio,
                            map_index,
                            frame_index,
                            rate,
                            algorithm,
                            0,
                            run_seed,
                        )
                        records.append(rec)
    return records, sample_frames


def summarize(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    def valid_mean(series):
        return float(series.dropna().mean()) if series.notna().any() else np.nan

    grouped = df.groupby(group_cols, dropna=False)
    rows = []
    for keys, group in grouped:
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = dict(zip(group_cols, keys))
        row.update(
            runs=len(group),
            reported_success_rate=float(group["reported_success"].mean()),
            valid_success_rate=float(group["valid_success"].mean()),
            invalid_report_rate=float(((group["reported_success"] == 1) & (group["valid_success"] == 0)).mean()),
            avg_runtime_s=float(group["runtime_s"].mean()),
            median_runtime_s=float(group["runtime_s"].median()),
            avg_geometric_length=valid_mean(group["geometric_length"]),
            avg_turning_points=valid_mean(group.loc[group["valid_success"] == 1, "turning_points"]),
            avg_safety_score=valid_mean(group.loc[group["valid_success"] == 1, "safety_score"]),
            avg_nodes_expanded=float(group["nodes_expanded"].mean()),
        )
        rows.append(row)
    return pd.DataFrame(rows)


def draw_map_samples(map_bank):
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2), constrained_layout=True)
    for ax, ratio in zip(axes, [0.15, 0.35, 0.55]):
        grid, corridor = map_bank[(ratio, 30, 0)]
        ax.imshow(grid, cmap="Greys", origin="upper", interpolation="nearest")
        xs = [p[0] for p in corridor]
        ys = [p[1] for p in corridor]
        ax.plot(xs, ys, color="#00a6a6", linewidth=1.5, label="保留连通走廊")
        ax.scatter([0, 29], [0, 29], c=["#2ca02c", "#d62728"], s=45, zorder=5)
        ax.set_title(f"目标障碍率 {ratio:.0%}\n实际 {np.mean(grid):.1%}")
        ax.set_xticks([])
        ax.set_yticks([])
    axes[0].legend(loc="lower right", fontsize=8)
    fig.suptitle("实验地图样例与复杂度分组", fontsize=15)
    fig.savefig(FIG_DIR / "图6-1_实验地图样例与复杂度分组.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def draw_path_comparison(map_bank, representative):
    grid, _ = map_bank[(0.35, 30, 0)]
    fig, axes = plt.subplots(2, 3, figsize=(12, 8), constrained_layout=True)
    for ax, algorithm in zip(axes.flat, ALGORITHM_ORDER):
        ax.imshow(grid, cmap="Greys", origin="upper", interpolation="nearest")
        path = representative.get(algorithm, [])
        valid, reason, _ = validate_path(
            grid,
            path,
            (0, 0),
            (29, 29),
            allow_line_segments=(algorithm == "混合优化算法"),
        )
        if path:
            xs = [p[0] for p in path]
            ys = [p[1] for p in path]
            ax.plot(xs, ys, color=COLORS[algorithm], linewidth=1.7)
        ax.scatter([0, 29], [0, 29], c=["#2ca02c", "#d62728"], s=35, zorder=5)
        status = "有效" if valid else f"无有效路径（{reason}）"
        ax.set_title(f"{ALGORITHM_LABELS[algorithm]}：{status}", fontsize=10)
        ax.set_xticks([])
        ax.set_yticks([])
    axes.flat[-1].axis("off")
    fig.suptitle("中复杂度地图上的五算法代表性路径", fontsize=15)
    fig.savefig(FIG_DIR / "图6-2_五算法代表性路径叠加对比.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def draw_runtime_distribution(static_df):
    fig, ax = plt.subplots(figsize=(9.5, 5.2), constrained_layout=True)
    data = [static_df.loc[static_df["algorithm"] == name, "runtime_s"].values for name in ALGORITHM_ORDER]
    bp = ax.boxplot(data, tick_labels=[ALGORITHM_LABELS[n] for n in ALGORITHM_ORDER], patch_artist=True, showfliers=False)
    for patch, name in zip(bp["boxes"], ALGORITHM_ORDER):
        patch.set_facecolor(COLORS[name])
        patch.set_alpha(0.65)
    ax.set_yscale("log")
    ax.set_ylabel("运行耗时 / s（对数坐标）")
    ax.set_title("五算法重复运行耗时分布")
    ax.grid(axis="y", alpha=0.25)
    fig.savefig(FIG_DIR / "图6-3_重复运行耗时分布.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def draw_metrics_and_failures(static_df):
    agg = summarize(static_df, ["algorithm"])
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    x = np.arange(len(ALGORITHM_ORDER))
    ordered = agg.set_index("algorithm").reindex(ALGORITHM_ORDER)
    axes[0, 0].bar(x, ordered["reported_success_rate"], color=[COLORS[n] for n in ALGORITHM_ORDER], alpha=0.45, label="算法报告成功率")
    axes[0, 0].bar(x, ordered["valid_success_rate"], color=[COLORS[n] for n in ALGORITHM_ORDER], alpha=0.9, width=0.55, label="合法路径成功率")
    axes[0, 0].set_xticks(x, [ALGORITHM_LABELS[n] for n in ALGORITHM_ORDER])
    axes[0, 0].set_ylim(0, 1.05)
    axes[0, 0].set_title("报告成功率与合法成功率")
    axes[0, 0].legend(fontsize=8)

    failures = static_df[static_df["valid_success"] == 0]
    counts = failures.groupby(["algorithm", "invalid_reason"]).size().unstack(fill_value=0).reindex(ALGORITHM_ORDER, fill_value=0)
    bottom = np.zeros(len(ALGORITHM_ORDER))
    for reason in counts.columns:
        values = counts[reason].values
        axes[0, 1].bar(x, values, bottom=bottom, label=reason)
        bottom += values
    axes[0, 1].set_xticks(x, [ALGORITHM_LABELS[n] for n in ALGORITHM_ORDER])
    axes[0, 1].set_title("未形成合法路径的原因")
    if len(counts.columns):
        axes[0, 1].legend(fontsize=8)

    valid_lengths = static_df[static_df["valid_success"] == 1]
    length_data = [valid_lengths.loc[valid_lengths["algorithm"] == n, "geometric_length"].dropna().values for n in ALGORITHM_ORDER]
    axes[1, 0].boxplot(length_data, tick_labels=[ALGORITHM_LABELS[n] for n in ALGORITHM_ORDER], showfliers=False)
    axes[1, 0].set_ylabel("几何路径长度")
    axes[1, 0].set_title("有效路径长度分布")

    success_by_ratio = static_df.groupby(["obstacle_target", "algorithm"])["valid_success"].mean().unstack().reindex(columns=ALGORITHM_ORDER)
    for name in ALGORITHM_ORDER:
        axes[1, 1].plot(success_by_ratio.index, success_by_ratio[name], marker="o", label=ALGORITHM_LABELS[name], color=COLORS[name])
    axes[1, 1].set_ylim(0, 1.05)
    axes[1, 1].set_xlabel("目标障碍率")
    axes[1, 1].set_ylabel("合法路径成功率")
    axes[1, 1].set_title("复杂度对成功率的影响")
    axes[1, 1].legend(fontsize=8)
    fig.suptitle("综合指标与失败分布", fontsize=15)
    fig.savefig(FIG_DIR / "图6-4_综合指标与失败分布.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def save_outputs(static_records, dynamic_records, representative, map_bank, sample_frames, elapsed):
    static_df = pd.DataFrame([asdict(r) for r in static_records])
    dynamic_df = pd.DataFrame([asdict(r) for r in dynamic_records])
    static_summary = summarize(static_df, ["obstacle_target", "width", "algorithm"])
    dynamic_summary = summarize(dynamic_df, ["dynamic_rate", "obstacle_target", "frame_index", "algorithm"])
    static_algo_summary = summarize(static_df, ["algorithm"])
    dynamic_algo_summary = summarize(dynamic_df, ["dynamic_rate", "algorithm"])

    static_df.to_csv(DATA_DIR / "静态实验逐次结果.csv", index=False, encoding="utf-8-sig")
    dynamic_df.to_csv(DATA_DIR / "动态实验逐次结果.csv", index=False, encoding="utf-8-sig")
    static_summary.to_csv(DATA_DIR / "静态实验分组汇总.csv", index=False, encoding="utf-8-sig")
    dynamic_summary.to_csv(DATA_DIR / "动态实验分组汇总.csv", index=False, encoding="utf-8-sig")

    with pd.ExcelWriter(DATA_DIR / "验证后实验结果.xlsx", engine="openpyxl") as writer:
        static_df.to_excel(writer, sheet_name="static_raw", index=False)
        dynamic_df.to_excel(writer, sheet_name="dynamic_raw", index=False)
        static_summary.to_excel(writer, sheet_name="static_summary", index=False)
        dynamic_summary.to_excel(writer, sheet_name="dynamic_summary", index=False)
        static_algo_summary.to_excel(writer, sheet_name="static_by_algorithm", index=False)
        dynamic_algo_summary.to_excel(writer, sheet_name="dynamic_by_algorithm", index=False)

    rep_json = {name: [[int(x), int(y)] for x, y in path] for name, path in representative.items()}
    (DATA_DIR / "代表性路径.json").write_text(json.dumps(rep_json, ensure_ascii=False, indent=2), encoding="utf-8")

    manifest = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "project_root": str(PROJECT),
        "elapsed_seconds": elapsed,
        "offline_only": True,
        "algorithm_config": {
            "A*": "project default",
            "ACO": {"n_ants": 10, "n_iterations": 20},
            "PSO": {"n_particles": 10, "n_iterations": 20},
            "SA": {"initial_temp": 100.0, "cooling_rate": 0.9, "min_temp": 0.01, "max_iter_per_temp": 10},
            "Hybrid": "project default: A* + line-of-sight smoothing",
        },
        "static_design": {"ratios": [0.15, 0.35, 0.55], "scales": [[30, 30], [50, 50]], "maps_per_cell": 10, "repeats": 3},
        "dynamic_design": {"ratios": [0.35, 0.55], "scale": [30, 30], "rates": [0.03, 0.08], "maps_per_cell": 5, "frames": 5, "repeats": 1},
        "validation": {
            "connected_corridor_reserved": True,
            "endpoint_check": True,
            "adjacency_check_for_grid_algorithms": True,
            "bresenham_collision_check_for_hybrid": True,
            "geometric_length": True,
        },
        "counts": {"static_records": len(static_df), "dynamic_records": len(dynamic_df)},
        "static_by_algorithm": static_algo_summary.replace({np.nan: None}).to_dict(orient="records"),
        "dynamic_by_algorithm": dynamic_algo_summary.replace({np.nan: None}).to_dict(orient="records"),
    }
    (DATA_DIR / "实验清单与汇总.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    np.savez_compressed(
        DATA_DIR / "实验地图样例.npz",
        low=map_bank[(0.15, 30, 0)][0],
        medium=map_bank[(0.35, 30, 0)][0],
        high=map_bank[(0.55, 30, 0)][0],
        dynamic_medium_rate003=np.stack(sample_frames[(0.03, 0.35)]),
        dynamic_high_rate008=np.stack(sample_frames[(0.08, 0.55)]),
    )

    draw_map_samples(map_bank)
    draw_path_comparison(map_bank, representative)
    draw_runtime_distribution(static_df)
    draw_metrics_and_failures(static_df)
    return static_algo_summary, dynamic_algo_summary


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    configure_fonts()
    started = time.perf_counter()
    print("[1/3] running 900 static algorithm executions...", flush=True)
    static_records, map_bank, representative = static_experiments()
    print("[2/3] running 500 dynamic-frame algorithm executions...", flush=True)
    dynamic_records, sample_frames = dynamic_experiments()
    elapsed = time.perf_counter() - started
    print("[3/3] saving validated data and figures...", flush=True)
    static_summary, dynamic_summary = save_outputs(
        static_records,
        dynamic_records,
        representative,
        map_bank,
        sample_frames,
        elapsed,
    )
    print(static_summary.to_string(index=False), flush=True)
    print(dynamic_summary.to_string(index=False), flush=True)
    print(f"completed in {elapsed:.2f}s", flush=True)


if __name__ == "__main__":
    main()
