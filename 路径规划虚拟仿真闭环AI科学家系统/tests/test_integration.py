# tests/test_integration.py

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import PathPlanningDecisionSystem
from agents.explanation_agent import ExplanationAgent


class TestIntegration:
    """端到端集成测试"""

    def test_full_decision_flow_low(self):
        system = PathPlanningDecisionSystem()
        env = {
            "obstacle_ratio": 0.10,
            "map_width": 100, "map_height": 100,
            "connectivity": 0.90, "topology_randomness": 0.20,
            "compute_limit": "high",
        }
        decision = system.decide(env)
        assert decision["scene_level"] == "低复杂度"
        assert decision["best_algorithm"] in ["A*", "ACO", "PSO", "SA", "混合优化算法"]
        assert len(decision["ranking"]) == 5
        assert decision["ranking"][0]["score"] >= decision["ranking"][-1]["score"]

    def test_full_decision_flow_high(self):
        system = PathPlanningDecisionSystem()
        env = {
            "obstacle_ratio": 0.62,
            "map_width": 100, "map_height": 100,
            "connectivity": 0.36, "topology_randomness": 0.72,
            "compute_limit": "high",
        }
        decision = system.decide(env)
        assert decision["scene_level"] == "高复杂度"

    def test_explanation_without_qwen(self):
        system = PathPlanningDecisionSystem()
        env = {
            "obstacle_ratio": 0.35,
            "map_width": 100, "map_height": 100,
            "connectivity": 0.68, "topology_randomness": 0.55,
            "compute_limit": "medium",
        }
        decision = system.decide(env)
        agent = ExplanationAgent(use_qwen=False)
        result = agent.explain(env, decision)
        assert "explanation_text" in result
        assert "当前场景等级" in result["explanation_text"]
        assert "选定最优算法名称" in result["explanation_text"]


def run_tests():
    """手动运行集成测试（不依赖 pytest）"""
    test = TestIntegration()
    test.test_full_decision_flow_low()
    test.test_full_decision_flow_high()
    test.test_explanation_without_qwen()
    print("所有集成测试通过！")


if __name__ == "__main__":
    run_tests()
