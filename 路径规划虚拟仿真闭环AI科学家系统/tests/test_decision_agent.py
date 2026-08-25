# tests/test_decision_agent.py

import pytest
from agents.decision_agent import DecisionAgent
from config import ALLOWED_ALGORITHMS


class TestDecisionAgent:
    def setup_method(self):
        self.agent = DecisionAgent()

    def test_select_best_normal(self):
        scored = [
            {"algorithm": "A*", "score": 0.95},
            {"algorithm": "ACO", "score": 0.80},
            {"algorithm": "PSO", "score": 0.75},
        ]
        env = {"scene_level": "低复杂度"}
        result = self.agent.select_best(env, scored)
        assert result["best_algorithm"] == "A*"
        assert result["scene_level"] == "低复杂度"

    def test_illegal_algorithm(self):
        scored = [{"algorithm": "Dijkstra", "score": 0.99}]
        env = {"scene_level": "低复杂度"}
        with pytest.raises(ValueError):
            self.agent.select_best(env, scored)

    def test_empty_records(self):
        with pytest.raises(ValueError):
            self.agent.select_best({"scene_level": "高复杂度"}, [])
