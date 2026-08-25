# tests/test_scoring.py

from config import WEIGHTS
from evaluation.scoring import get_weights, normalize_reverse, compute_score


class TestScoring:
    def test_weights_low_complexity(self):
        env = {"scene_level": "低复杂度", "compute_limit": "high"}
        w = get_weights(env)
        assert w == WEIGHTS["低复杂度"]

    def test_weights_low_compute_adjust(self):
        env = {"scene_level": "低复杂度", "compute_limit": "low"}
        w = get_weights(env)
        assert w["time"] > WEIGHTS["低复杂度"]["time"]

    def test_normalize_reverse(self):
        assert normalize_reverse(0, 0, 10) == 1.0
        assert normalize_reverse(10, 0, 10) == 0.0
        assert normalize_reverse(5, 0, 10) == 0.5

    def test_normalize_reverse_equal(self):
        assert normalize_reverse(5, 5, 5) == 1.0

    def test_compute_score_basic(self):
        record = {
            "avg_time": 1.0,
            "avg_path_length": 100.0,
            "success_rate": 0.9,
            "stability_score": 0.8,
            "penalty": 0.0,
        }
        weights = WEIGHTS["低复杂度"]
        score = compute_score(record, weights, 0.0, 2.0, 80.0, 120.0)
        assert isinstance(score, float)
        assert 0 <= score <= 1.0
