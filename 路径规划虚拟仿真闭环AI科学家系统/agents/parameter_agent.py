# agents/parameter_agent.py — 算法参数推荐智能体

# 各种算法在不同算力等级下的迭代/种群缩放比例
_COMPUTE_SCALE = {
    "low": 0.4,
    "medium": 0.7,
    "high": 1.0,
}


class ParameterAgent:
    """根据选定的算法与环境输入，推荐对应的运行参数"""

    def recommend(self, env_input: dict, decision: dict) -> dict:
        best = decision.get("best_algorithm", "")
        compute_limit = env_input.get("compute_limit", "medium")
        scale = _COMPUTE_SCALE.get(compute_limit, 1.0)

        if best == "A*":
            return {
                "heuristic": "manhattan",
                "diagonal": False,
                "weight": 1.0,
            }

        if best == "ACO":
            return {
                "n_ants": max(10, int(50 * scale)),
                "alpha": 1.0,
                "beta": 2.0,
                "evaporation": 0.1,
                "iterations": max(20, int(100 * scale)),
            }

        if best == "PSO":
            return {
                "n_particles": max(10, int(30 * scale)),
                "w": 0.7,
                "c1": 1.5,
                "c2": 1.5,
                "iterations": max(20, int(100 * scale)),
            }

        if best == "SA":
            return {
                "T_init": 100.0,
                "T_min": 1.0,
                "alpha": 0.95,
                "iterations": max(50, int(500 * scale)),
            }

        if best == "混合优化算法":
            return {
                "aco_weight": 0.5,
                "sa_weight": 0.3,
                "pso_weight": 0.2,
                "iterations": max(20, int(80 * scale)),
            }

        return {}
