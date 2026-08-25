# main.py — 主入口，串联完整决策流程

from agents.data_agent import DataReceiverAgent
from agents.environment_agent import EnvironmentAgent
from agents.knowledge_agent import KnowledgeRetrievalAgent
from agents.rule_agent import RuleConstraintAgent
from agents.evaluation_agent import AlgorithmEvaluationAgent
from agents.decision_agent import DecisionAgent


class PathPlanningDecisionSystem:
    """路径规划算法自适应选型系统——核心决策引擎"""

    def __init__(self):
        self.data_agent = DataReceiverAgent()
        self.env_agent = EnvironmentAgent()
        self.knowledge_agent = KnowledgeRetrievalAgent()
        self.rule_agent = RuleConstraintAgent()
        self.eval_agent = AlgorithmEvaluationAgent()
        self.decision_agent = DecisionAgent()

    def decide(self, env_input: dict) -> dict:
        """执行完整决策流程，返回决策结果"""
        env = self.data_agent.validate(env_input)
        env = self.env_agent.classify(env)
        records = self.knowledge_agent.retrieve(env["scene_level"])
        records = self.rule_agent.filter_and_penalize(env, records)
        scored = self.eval_agent.score(env, records)
        decision = self.decision_agent.select_best(env, scored)
        return decision


def main():
    """Phase 1 验证：使用三组测试数据验证决策输出"""
    test_cases = [
        {
            "name": "低复杂度场景",
            "input": {
                "obstacle_ratio": 0.10,
                "map_width": 100, "map_height": 100,
                "connectivity": 0.90,
                "topology_randomness": 0.20,
                "compute_limit": "high",
            },
        },
        {
            "name": "中复杂度场景",
            "input": {
                "obstacle_ratio": 0.35,
                "map_width": 100, "map_height": 100,
                "connectivity": 0.68,
                "topology_randomness": 0.55,
                "compute_limit": "medium",
            },
        },
        {
            "name": "高复杂度场景（算力充足）",
            "input": {
                "obstacle_ratio": 0.62,
                "map_width": 100, "map_height": 100,
                "connectivity": 0.36,
                "topology_randomness": 0.72,
                "compute_limit": "high",
            },
        },
    ]

    system = PathPlanningDecisionSystem()

    for case in test_cases:
        decision = system.decide(case["input"])
        ranking = decision["ranking"]

        print(f"\n{'='*60}")
        print(f"  {case['name']}")
        print(f"{'='*60}")
        print(f"当前场景等级：{decision['scene_level']}")
        print(f"选定最优算法名称：{decision['best_algorithm']}")
        print(f"综合得分：{decision['best_score']}")
        print(f"\n排名详情：")
        for i, r in enumerate(ranking, 1):
            bar = "█" * int(r["score"] * 20)
            print(f"  {i}. {r['algorithm']:<6}  得分={r['score']:.4f}  {bar}")
            d = r["detail"]
            print(f"     耗时={d['time_score']:.3f}  路径={d['length_score']:.3f}  "
                  f"成功率={d['success_score']:.3f}  稳定性={d['stability_score']:.3f}  "
                  f"惩罚={d['penalty']:.3f}")


if __name__ == "__main__":
    main()
