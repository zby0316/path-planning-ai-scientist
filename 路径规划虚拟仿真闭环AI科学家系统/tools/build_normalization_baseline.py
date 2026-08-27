# tools/build_normalization_baseline.py — 生成归一化基准集
"""在固定的离线参考场景网格上预生成各场景等级的九维指标归一化区间。

产出 knowledge_base/normalization_baseline.json，供 scoring.load_range_dict 使用：
评分归一化不再依赖当批候选的 min/max，跨场景/跨批次分数可比。

用法：
    python tools/build_normalization_baseline.py            # 标准档（3 等级 × 2 尺度 × 5 图）
    python tools/build_normalization_baseline.py --quick    # 快速档（3 等级 × 1 尺度 × 3 图）
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import NORMALIZATION_BASELINE_PATH, SCORING_METRIC_KEYS
from evaluation.benchmark import ALGORITHM_FACTORIES
from evaluation.metrics import evaluate_algorithm
from map.map_generator import MapGenerator

# 参考场景矩阵（与证据库旁路脚本的种子约定对齐）
SCENE_LEVELS = [
    ("低复杂度", 0.10),
    ("中复杂度", 0.35),
    ("高复杂度", 0.65),
]
SCALES = [(50, 50), (100, 100)]
BASE_SEED = 2026071100

# evaluate_algorithm 返回字段 → SCORING_METRIC_KEYS 指标名
_METRIC_FIELD_MAP = {
    "time": "avg_time",
    "path_length": "avg_path_length",
    "success_rate": "success_rate",
    "stability": "stability_score",
    "smoothness": "smoothness",
    "safety_score": "safety_score",
    "expanded_nodes": "expanded_nodes",
    "compute_cost": "compute_cost",
    "robustness": "robustness",
}


def _build_monotone_corridor(w: int, h: int, rng) -> list:
    """随机单调走廊 (0,0)→(w-1,h-1)：保底连通路径（移植自证据库验证脚本）。"""
    x, y = 0, 0
    corridor = [(x, y)]
    while x < w - 1 or y < h - 1:
        if x == w - 1:
            y += 1
        elif y == h - 1:
            x += 1
        elif rng.random() < 0.5:
            x += 1
        else:
            y += 1
        corridor.append((x, y))
    return corridor


def _generate_solvable_map(seed: int, w: int, h: int, obstacle_ratio: float):
    """生成保证起终点连通的参考地图。

    高障碍率（>0.5）下随机布障超过方格点渗流阈值，起终点几乎必然不连通，
    因此先铺设单调保底走廊再布障（与 evidence/validated_experiments 的
    生成方式一致）。基准集锚定算法能力空间，而非地图可解性。
    """
    rng = np.random.RandomState(seed)
    corridor = _build_monotone_corridor(w, h, rng)
    reserved = {y * w + x for x, y in corridor}
    available = [idx for idx in range(w * h) if idx not in reserved]
    obstacle_count = min(int(round(w * h * obstacle_ratio)), len(available))
    chosen = rng.choice(available, size=obstacle_count, replace=False)
    grid = np.zeros((h, w), dtype=np.int8)
    grid.flat[chosen] = 1
    return grid, (0, 0), (w - 1, h - 1)


def build_baseline(n_maps: int, scales: list, n_runs: int, compute_limit: str) -> dict:
    # per_level[scene][metric][algo] -> list of values (跨尺度/地图)
    per_level = {name: {m: {} for m in SCORING_METRIC_KEYS} for name, _ in SCENE_LEVELS}

    for level_idx, (level_name, obstacle_ratio) in enumerate(SCENE_LEVELS):
        for scale_idx, (w, h) in enumerate(scales):
            for map_idx in range(n_maps):
                seed = BASE_SEED + level_idx * 10000 + scale_idx * 1000 + map_idx
                grid, start, target = _generate_solvable_map(seed, w, h, obstacle_ratio)

                for algo_index, (algo_name, factory) in enumerate(ALGORITHM_FACTORIES.items()):
                    metrics = evaluate_algorithm(
                        factory, grid, start, target,
                        n_runs=n_runs, compute_limit=compute_limit,
                        base_seed=seed, algo_index=algo_index,
                        algorithm_name=algo_name,
                    )
                    for metric, field in _METRIC_FIELD_MAP.items():
                        per_level[level_name][metric].setdefault(algo_name, []).append(
                            float(metrics.get(field, 0.0) or 0.0)
                        )

    # 每等级：先按算法求均值（与知识库记录口径一致），再跨算法取 min/max
    scene_levels = {}
    for level_name, metrics_map in per_level.items():
        ranges = {}
        for metric, by_algo in metrics_map.items():
            algo_means = [
                sum(vals) / len(vals) for vals in by_algo.values() if vals
            ]
            if not algo_means:
                ranges[metric] = [0.0, 1.0]
            else:
                ranges[metric] = [
                    round(min(algo_means), 6),
                    round(max(algo_means), 6),
                ]
        scene_levels[level_name] = ranges

    return scene_levels


def main():
    parser = argparse.ArgumentParser(description="生成归一化基准集")
    parser.add_argument("--quick", action="store_true", help="快速档：1 尺度 × 3 图")
    parser.add_argument("--n-maps", type=int, default=5, help="每个 (等级, 尺度) 的地图数")
    parser.add_argument("--n-runs", type=int, default=3, help="每算法重复次数")
    parser.add_argument("--compute-limit", default="medium", choices=["low", "medium", "high"])
    parser.add_argument("--out", default=NORMALIZATION_BASELINE_PATH)
    args = parser.parse_args()

    scales = [(50, 50)] if args.quick else SCALES
    n_maps = 3 if args.quick else args.n_maps

    print(f"[baseline] 参考矩阵：{len(SCENE_LEVELS)} 等级 × {len(scales)} 尺度 × "
          f"{n_maps} 图 × 5 算法 × {args.n_runs} 重复（compute={args.compute_limit}）")
    t0 = time.perf_counter()
    scene_levels = build_baseline(n_maps, scales, args.n_runs, args.compute_limit)
    elapsed = time.perf_counter() - t0

    payload = {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "mode": "reference_scenarios",
        "compute_limit": args.compute_limit,
        "n_runs_per_algo": args.n_runs,
        "maps_per_config": n_maps,
        "scales": [list(s) for s in scales],
        "base_seed": BASE_SEED,
        "elapsed_seconds": round(elapsed, 1),
        "metric_keys": list(SCORING_METRIC_KEYS),
        "scene_levels": scene_levels,
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[baseline] 完成，耗时 {elapsed:.1f}s → {args.out}")
    for name, ranges in scene_levels.items():
        print(f"  {name}: time={ranges['time']}, success_rate={ranges['success_rate']}")


if __name__ == "__main__":
    main()
