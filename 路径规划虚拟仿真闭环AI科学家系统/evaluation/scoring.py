# evaluation/scoring.py — 评分函数（10 维扩展版）

from config import (
    WEIGHTS,
    COMPUTE_LIMIT_WEIGHT_ADJUST,
    NORMALIZATION_DIRECTION,
    SCORING_METRIC_KEYS,
)


def get_weights(env: dict) -> dict:
    """根据场景等级和算力限制获取权重"""
    weights = WEIGHTS[env["scene_level"]].copy()
    if env.get("compute_limit") == "low":
        for key, adj in COMPUTE_LIMIT_WEIGHT_ADJUST.items():
            weights[key] = weights.get(key, 0) + adj
    return weights


def normalize_reverse(value: float, min_value: float, max_value: float) -> float:
    """逆向归一化：值越小得分越高（用于耗时、路径长度）"""
    if max_value == min_value:
        return 1.0
    score = 1.0 - (value - min_value) / (max_value - min_value)
    return float(max(0.0, min(1.0, score)))


def normalize_forward(value: float, min_value: float, max_value: float) -> float:
    """正向归一化：值越大得分越高（用于成功率、安全分等）"""
    if max_value == min_value:
        return 1.0
    score = (value - min_value) / (max_value - min_value)
    return float(max(0.0, min(1.0, score)))


def _record_metric_range(records: list, key: str) -> tuple:
    vals = [r.get(key, 0.0) for r in records]
    if not vals:
        return (0.0, 1.0)
    return (min(vals), max(vals))


def compute_score(
    record: dict,
    weights: dict,
    min_time: float = 0.0,
    max_time: float = 0.0,
    min_length: float = 0.0,
    max_length: float = 0.0,
    range_dict: dict = None,
) -> float:
    """根据权重计算单个算法的综合得分

    兼容旧 API（4 维，min_time/max_time/min_length/max_length）
    与新 API（range_dict 提供 9 个指标的 (min, max)）
    """
    time_score = normalize_reverse(record.get("avg_time", 0.0), min_time, max_time)
    length_score = normalize_reverse(record.get("avg_path_length", 0.0), min_length, max_length)
    success_score = float(record.get("success_rate", 0.0))
    stability_score = float(record.get("stability_score", 0.0))

    total = (
        weights.get("time", 0) * time_score
        + weights.get("path_length", 0) * length_score
        + weights.get("success_rate", 0) * success_score
        + weights.get("stability", 0) * stability_score
    )

    if range_dict:
        metric_to_key = {
            "smoothness": "smoothness",
            "safety_score": "safety_score",
            "expanded_nodes": "expanded_nodes",
            "compute_cost": "compute_cost",
            "robustness": "robustness",
        }
        for metric, rkey in metric_to_key.items():
            if metric not in weights:
                continue
            lo, hi = range_dict.get(metric, (0.0, 1.0))
            val = float(record.get(rkey, 0.0))
            direction = NORMALIZATION_DIRECTION.get(metric, "forward")
            if direction == "reverse":
                sub_score = normalize_reverse(val, lo, hi)
            else:
                sub_score = normalize_forward(val, lo, hi)
            total += weights[metric] * sub_score

    total -= record.get("penalty", 0)
    return round(float(max(0.0, min(1.0, total))), 4)


def compute_score_detail(record: dict, weights: dict, range_dict: dict) -> dict:
    """为单条记录计算 10 维子指标得分与加权综合分，返回详情"""
    detail = {}
    for metric in SCORING_METRIC_KEYS:
        if metric not in weights:
            continue
        lo, hi = range_dict.get(metric, (0.0, 1.0))
        val = float(record.get(metric, 0.0))
        direction = NORMALIZATION_DIRECTION.get(metric, "forward")
        if direction == "reverse":
            sub = normalize_reverse(val, lo, hi)
        else:
            sub = normalize_forward(val, lo, hi)
        detail[f"{metric}_score"] = round(sub, 4)

    detail["penalty"] = record.get("penalty", 0)
    detail["time_score"] = detail.get("time_score", 0.0)
    detail["length_score"] = detail.get("path_length_score", 0.0)
    detail["success_score"] = detail.get("success_rate_score", 0.0)
    detail["stability_score"] = detail.get("stability_score", 0.0)

    final = sum(
        weights[k] * detail.get(f"{k}_score", 0.0)
        for k in weights.keys()
    ) - detail["penalty"]
    detail["final_score"] = round(float(max(0.0, min(1.0, final))), 4)
    return detail


def compute_scores(records: list, weights: dict) -> list:
    """批量评分：按 SCORING_METRIC_KEYS 计算 min/max 区间，再加权"""
    range_dict = {}
    for metric in SCORING_METRIC_KEYS:
        range_dict[metric] = _record_metric_range(records, metric)

    scored = []
    for record in records:
        detail = compute_score_detail(record, weights, range_dict)
        record = record.copy()
        record["score"] = detail["final_score"]
        record["detail"] = detail
        scored.append(record)

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored
