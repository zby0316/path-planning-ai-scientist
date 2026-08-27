# tests/test_scoring_baseline.py — 基准集归一化回归

import json
import os
import tempfile

import pytest

from evaluation import scoring
from evaluation.scoring import load_range_dict


@pytest.fixture()
def baseline_env(tmp_path, monkeypatch):
    """构造一个临时基准集文件并让 scoring 重新加载。"""
    payload = {
        "version": 1,
        "scene_levels": {
            "低复杂度": {
                "time": [0.001, 1.0],
                "path_length": [50.0, 150.0],
                "success_rate": [0.5, 1.0],
                "stability": [0.0, 1.0],
                "smoothness": [0.0, 0.5],
                "safety_score": [0.0, 1.0],
                "expanded_nodes": [10, 10000],
                "compute_cost": [0.0, 1.0],
                "robustness": [0.0, 1.0],
            }
        },
    }
    path = tmp_path / "normalization_baseline.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(scoring, "NORMALIZATION_BASELINE_PATH", str(path))
    monkeypatch.setattr(scoring, "_baseline_cache", None)
    return payload


class TestLoadRangeDict:
    def test_baseline_hit(self, baseline_env):
        range_dict, source = load_range_dict("低复杂度")
        assert source == "baseline"
        assert range_dict["time"] == [0.001, 1.0]

    def test_missing_scene_falls_back_to_batch(self, baseline_env):
        records = [{"avg_time": 0.1}, {"avg_time": 0.5}]
        range_dict, source = load_range_dict("高复杂度", records=records)
        assert source == "batch_fallback"
        assert range_dict["time"] == (0.1, 0.5)

    def test_missing_file_falls_back(self, tmp_path, monkeypatch):
        monkeypatch.setattr(scoring, "NORMALIZATION_BASELINE_PATH", str(tmp_path / "nope.json"))
        monkeypatch.setattr(scoring, "_baseline_cache", None)
        records = [{"avg_time": 0.2}]
        _, source = load_range_dict("低复杂度", records=records)
        assert source == "batch_fallback"


class TestBaselineScoreStability:
    def test_scores_invariant_to_candidate_set(self, baseline_env):
        """基准集模式下：候选集增删不影响剩余候选的相对分差语义。

        同一条记录在两个不同候选批次中应得到相同的基础分
        （penalty 项除外，此处不带 penalty）。
        """
        from agents.evaluation_agent import AlgorithmEvaluationAgent

        agent = AlgorithmEvaluationAgent()
        env = {"scene_level": "低复杂度", "compute_limit": "high"}

        record_fast = {
            "algorithm": "A*", "avg_time": 0.01, "avg_path_length": 60.0,
            "success_rate": 1.0, "stability_score": 0.9,
        }
        record_slow = {
            "algorithm": "ACO", "avg_time": 0.8, "avg_path_length": 120.0,
            "success_rate": 0.7, "stability_score": 0.5,
        }

        # 批次 1：两个候选
        scored1 = agent.score(env, [dict(record_fast), dict(record_slow)])
        by_algo1 = {r["algorithm"]: r for r in scored1}

        # 批次 2：只评单个候选
        scored2 = agent.score(env, [dict(record_slow)])
        by_algo2 = {r["algorithm"]: r for r in scored2}

        assert by_algo1["ACO"]["normalization_source"] == "baseline"
        # ACO 在两批次中的分数一致（基准集锚定，不受当批候选影响）
        assert by_algo1["ACO"]["score"] == by_algo2["ACO"]["score"]
        # 快算法在基准集下得分更高
        assert by_algo1["A*"]["score"] > by_algo1["ACO"]["score"]

    def test_batch_mode_restores_old_behavior(self, baseline_env, monkeypatch):
        """NORMALIZATION_MODE=batch 时退回当批 min/max。"""
        monkeypatch.setattr(scoring, "NORMALIZATION_MODE", "batch")
        records = [{"avg_time": 0.1}, {"avg_time": 0.5}]
        _, source = load_range_dict("低复杂度", records=records)
        assert source == "batch_fallback"
