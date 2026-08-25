"""手工运行完整多智能体流水线（含 LLM 智能体）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agents.orchestrator_agent import OrchestratorAgent
from agents.pipeline import ScientificDiscoveryPipeline

# ====== 测试 1: OrchestratorAgent（12+ 智能体流水线）====== 
print("=" * 70)
print("  测试 1: OrchestratorAgent — 12+ 智能体流水线")
print("=" * 70)

orchestrator = OrchestratorAgent(use_qwen=True)
env_input = {
    "obstacle_ratio": 0.35,
    "map_width": 100, "map_height": 100,
    "connectivity": 0.68,
    "topology_randomness": 0.55,
    "compute_limit": "medium",
    "start_point": [10, 10],
    "target_point": [90, 90],
    "dynamic_change_rate": 0.0,
    "optimization_preference": "balanced",
}

state = orchestrator.run(env_input)

print(f"\n场景等级: {state.decision.get('scene_level')}")
print(f"最优算法: {state.decision.get('best_algorithm')}")
print(f"综合得分: {state.decision.get('best_score'):.4f}")

if state.metadata and state.metadata.get("explanation"):
    exp = state.metadata["explanation"]
    if isinstance(exp, dict):
        print(f"\n📝 LLM 解释（前200字）: {exp.get('explanation_text', '')[:200]}...")

if state.hypothesis and state.hypothesis.get("hypothesis_text"):
    print(f"\n🔬 LLM 假设（前200字）: {state.hypothesis['hypothesis_text'][:200]}...")

if state.metadata and state.metadata.get("errors"):
    print(f"\n⚠️ 流水线错误: {state.metadata['errors']}")
else:
    print("\n✅ 流水线无错误，所有智能体执行成功！")

# ====== 测试 2: ScientificDiscoveryPipeline（假设-验证-反思闭环）====== 
print("\n\n" + "=" * 70)
print("  测试 2: ScientificDiscoveryPipeline — 假设-验证-反思闭环")
print("=" * 70)

pipeline = ScientificDiscoveryPipeline(use_qwen=True)
state2 = pipeline.run_full_cycle(env_input, max_iterations=1)

print(f"\n场景等级: {state2.decision.get('scene_level')}")
print(f"最优算法: {state2.decision.get('best_algorithm')}")

if state2.metadata and state2.metadata.get("iterations"):
    for it in state2.metadata["iterations"]:
        print(f"\n迭代 {it['iteration']}:")
        print(f"  假设摘要: {it['hypothesis_summary'][:150]}...")
        print(f"  置信度: {it['confidence_score']:.3f}")

if state2.reflection:
    print(f"\n🔄 反思结果: {state2.reflection.get('summary', '')[:200]}...")

print("\n✅ 完整流水线测试完成！")
