# tests/test_environment_agent.py

import pytest
from agents.environment_agent import EnvironmentAgent


class TestEnvironmentAgent:
    def setup_method(self):
        self.agent = EnvironmentAgent()

    def test_low_complexity(self):
        env = {"obstacle_ratio": 0.10}
        result = self.agent.classify(env)
        assert result["scene_level"] == "低复杂度"

    def test_medium_complexity(self):
        env = {"obstacle_ratio": 0.35}
        result = self.agent.classify(env)
        assert result["scene_level"] == "中复杂度"

    def test_high_complexity(self):
        env = {"obstacle_ratio": 0.62}
        result = self.agent.classify(env)
        assert result["scene_level"] == "高复杂度"

    def test_boundary_low(self):
        env = {"obstacle_ratio": 0.199}
        result = self.agent.classify(env)
        assert result["scene_level"] == "低复杂度"

    def test_boundary_medium(self):
        env = {"obstacle_ratio": 0.20}
        result = self.agent.classify(env)
        assert result["scene_level"] == "中复杂度"

    def test_boundary_high(self):
        env = {"obstacle_ratio": 0.501}
        result = self.agent.classify(env)
        assert result["scene_level"] == "高复杂度"
