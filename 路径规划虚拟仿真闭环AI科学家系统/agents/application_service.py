"""统一的当前地图实验与决策服务。"""
from __future__ import annotations

import hashlib
import inspect
import time
import uuid

import numpy as np

from agents.data_agent import DataReceiverAgent
from agents.environment_agent import EnvironmentAgent
from agents.evaluation_agent import AlgorithmEvaluationAgent
from agents.knowledge_agent import KnowledgeRetrievalAgent
from agents.rule_agent import RuleConstraintAgent
from config import ALLOWED_ALGORITHMS
from data.experiment_db import ExperimentDB
from evaluation.benchmark import BenchmarkRunner
from map.connectivity_checker import ConnectivityChecker, free_space_connectivity_ratio, topology_randomness
from map.map_generator import MapGenerator
from algorithms.astar import AStar
from algorithms.aco import AntColony
from algorithms.pso import ParticleSwarm
from algorithms.sa import SimulatedAnnealing
from algorithms.hybrid import HybridAlgorithm


class ApplicationService:
    """运行先验、当前地图实验、决策和可证伪检查。"""

    def __init__(self, db_path=None, benchmark=None):
        self.db_path = db_path
        self.benchmark = benchmark or BenchmarkRunner()

    def run(self, env_input, grid=None, n_runs=3, time_budget_s=1.0, expected_algorithm=None):
        started = time.perf_counter()
        env = dict(env_input or {})
        width, height = int(env.get('map_width', 30)), int(env.get('map_height', 30))
        seed = int(env.get('random_seed', 42))
        start = tuple(env.get('start_point') or [0, 0])
        target = tuple(env.get('target_point') or [width - 1, height - 1])
        if width <= 0 or height <= 0 or n_runs < 1 or time_budget_s <= 0:
            raise ValueError('地图尺寸、重复次数和运行预算必须为正数')
        if not 0 <= float(env.get('obstacle_ratio', .15)) <= 1:
            raise ValueError('障碍物占比必须在 0 到 1 之间')
        if env.get('optimization_preference', '平衡模式') not in ('平衡模式', '耗时优先', '成功率优先', '路径最短'):
            raise ValueError('不支持的优化偏好')
        for p in (start, target):
            if len(p) != 2 or any(not isinstance(v, (int, np.integer)) or isinstance(v, bool) for v in p) or not (0 <= p[0] < width and 0 <= p[1] < height):
                raise ValueError('起终点坐标无效或越界')
        if grid is None:
            grid = MapGenerator(seed=seed).generate(width, height, float(env.get('obstacle_ratio', .15)), start, target)
        grid = np.asarray(grid)
        if grid.ndim != 2 or grid.shape != (height, width) or not np.isin(grid, [0, 1]).all():
            raise ValueError('地图必须为尺寸匹配的二维 0/1 栅格')
        grid = grid.astype(np.uint8, copy=True)
        for p in (start, target):
            if len(p) != 2 or any(not isinstance(v, (int, np.integer)) or isinstance(v, bool) for v in p) or not (0 <= p[0] < width and 0 <= p[1] < height):
                raise ValueError('起终点坐标无效或越界')
            if grid[p[1], p[0]] != 0:
                raise ValueError('起终点不能位于障碍物')
        if not ConnectivityChecker().is_reachable(grid, start, target):
            raise ValueError('起点与终点不连通')
        dynamic_rate = float(env.get('dynamic_change_rate', 0) or 0)
        if not 0 <= dynamic_rate <= 1:
            raise ValueError('动态变化率必须在 0 到 1 之间')
        steps = int(env.get('dynamic_steps', 2)) if dynamic_rate else 1
        if not 1 <= steps <= 10:
            raise ValueError('动态时间片数量必须在 1 到 10 之间')
        grids = [grid]
        if dynamic_rate:
            generator = MapGenerator(seed=int(env.get('map_seed', seed)))
            for _ in range(1, steps):
                grids.append(generator.perturb_dynamic_obstacles(grids[-1], dynamic_rate, start, target))
        env.update(map_width=width, map_height=height, start_point=list(start), target_point=list(target),
                   obstacle_ratio=float(np.mean(grid == 1)), connectivity=free_space_connectivity_ratio(grid),
                   topology_randomness=topology_randomness(grid), random_seed=seed,
                   compute_limit=env.get('compute_limit', 'medium'))
        env = EnvironmentAgent().classify(DataReceiverAgent().validate(env))
        evaluator = AlgorithmEvaluationAgent()
        historical = KnowledgeRetrievalAgent().retrieve(env['scene_level'])
        prior = evaluator.score(env, RuleConstraintAgent().filter_and_penalize(env, historical))
        if not prior:
            raise ValueError('缺少历史先验证据')
        prior_best = prior[0]['algorithm']
        candidate = expected_algorithm or prior_best
        hypothesis = {'hypothesis_text': f'在当前地图上 {candidate} 的有效成功率不低于其他算法。',
                      'variable': '算法', 'control': [r['algorithm'] for r in prior if r['algorithm'] != candidate],
                      'threshold': 0.0, 'falsification': '存在对照算法有效成功率更高',
                      'expected_algorithm': candidate}
        t_experiment = time.perf_counter()
        runner = self.benchmark.run_dynamic_sequence if dynamic_rate else self.benchmark.run
        results = runner(grids if dynamic_rate else grid, start, target, n_runs=n_runs, compute_limit=env['compute_limit'], base_seed=seed, time_budget_s=time_budget_s)
        if (len(results) != len(ALLOWED_ALGORITHMS) or
                {r.get('algorithm') for r in results} != set(ALLOWED_ALGORITHMS) or
                any(len(r.get('runs', [])) != n_runs * steps for r in results)):
            raise RuntimeError('五算法实验未完整完成')
        with ExperimentDB(self.db_path) as db:
            map_id = db.insert_map(source='application_service', map_type='dynamic_grid' if dynamic_rate else 'grid', width=width, height=height,
                                   obstacle_ratio=env['obstacle_ratio'], connectivity=env['connectivity'], topology_randomness=env['topology_randomness'], dynamic_change_rate=dynamic_rate)
            db.save_map_grid(map_id, grid)
            for record in results:
                record['run_id'] = db.record_benchmark_run(map_id, record['algorithm'], record,
                    parameters={'seed': seed, 'n_runs': n_runs, 'time_budget_s': time_budget_s, 'start': start, 'target': target, 'dynamic_steps': steps, 'dynamic_change_rate': dynamic_rate},
                    compute_limit=env['compute_limit'], seed=seed)
        eligible = [r for r in results if any(run.get('valid_success') for run in r['runs'])]
        experiment_elapsed = time.perf_counter() - t_experiment
        weights = evaluator.get_weights(env)
        pref = env.get('optimization_preference', '平衡模式')
        key = {'耗时优先': 'time', '成功率优先': 'success_rate', '路径最短': 'path_length'}.get(pref)
        if key:
            weights[key] += 0.25
            total = sum(weights.values())
            weights = {k: v / total for k, v in weights.items()}
        from evaluation.scoring import load_range_dict, compute_score_detail
        ranges, source = load_range_dict(env['scene_level'], records=eligible)
        ranking = []
        for record in RuleConstraintAgent().filter_and_penalize(env, eligible):
            detail = compute_score_detail(record, weights, ranges)
            ranking.append({**record, 'detail': detail, 'score': detail['final_score'], 'normalization_source': source})
        ranking.sort(key=lambda r: r['score'], reverse=True)
        sufficient = bool(ranking) and all(
            not any(str(x.get('invalid_reason', '')).startswith('exception:')
                    for x in r['runs'] + r.get('robustness_runs', []))
            for r in results)
        best = ranking[0]['algorithm'] if sufficient else None
        candidate_rate = next(r['success_rate'] for r in results if r['algorithm'] == candidate)
        supported = candidate_rate >= max(r['success_rate'] for r in results) if sufficient else None
        result = {'status': 'completed' if sufficient else 'insufficient_evidence', 'env_input': env,
                  'map_id': map_id, 'map_sha256': hashlib.sha256(grid.tobytes()).hexdigest(),
                  'prior_ranking': prior, 'decision': {'scene_level': env['scene_level'], 'best_algorithm': best,
                    'best_score': ranking[0]['score'] if best else None, 'ranking': ranking,
                    'need_human_check': not sufficient or len(ranking) < 2 or ranking[0]['score'] - ranking[1]['score'] < .05},
                  'weights': weights, 'experiment_results': results, 'hypothesis': hypothesis,
                  'hypothesis_supported': supported, 'reflection': {'stop_reason': '当前地图验证完成；跨地图推广仍需独立实验',
                    'issues': ['当前仅一张地图，不能推断跨地图泛化'], 'run_ids': [r['run_id'] for r in results]},
                  'human_feedback': env.get('human_feedback', ''), 'degraded': ['离线模式：未调用大模型和联网文献检索'],
                  'previous_decision': env.get('previous_decision'),
                  'previous_cycle_id': env.get('previous_cycle_id'),
                  'dynamic_steps': steps,
                  'frame_sha256': [hashlib.sha256(frame.tobytes()).hexdigest() for frame in grids],
                  'timings': {'experiment_seconds': round(experiment_elapsed, 4)}}
        classes = {'A*': AStar, 'ACO': AntColony, 'PSO': ParticleSwarm,
                   'SA': SimulatedAnnealing, '混合优化算法': HybridAlgorithm}
        result['experiment_parameters'] = {
            name: {**{key: param.default for key, param in inspect.signature(cls).parameters.items()
                      if param.default is not inspect.Parameter.empty and key not in ('seed', 'time_budget_s')},
                   'time_budget_s': time_budget_s, 'seed': '见逐次记录'}
            for name, cls in classes.items()
        }
        result['decision']['change_reason'] = ('当前地图实验按显示的权重与归一化基准重新评分；'
                                                f'先验推荐为 {prior_best}，最终推荐为 {best or "无"}。')
        result['decision']['prior_best_algorithm'] = prior_best
        result['decision']['evidence_source'] = '当前地图独立校验实验'
        result['report'] = render_report(result)
        result['timings']['total_seconds'] = round(time.perf_counter() - started, 4)
        if result['timings']['total_seconds'] > 60:
            result['status'] = 'budget_exceeded'
            result['decision']['best_algorithm'] = None
            result['decision']['best_score'] = None
            result['decision']['need_human_check'] = True
            result['decision']['change_reason'] = '总耗时超过离线演示预算，暂不输出最终推荐。'
            result['hypothesis_supported'] = None
            result['reflection']['stop_reason'] = '超过离线演示时间预算，结论未完成'
        result['cycle_id'] = 'cycle_' + uuid.uuid4().hex
        result['report'] = render_report(result)
        with ExperimentDB(self.db_path) as db:
            db.save_research_cycle(result['cycle_id'], map_id, result['status'], result)
        return result

    def run_cycle(self, env_input, grid=None, max_iterations=1, n_runs=3, time_budget_s=1.0):
        """重复验证被反驳的候选，每轮使用独立算法种子并记录停止原因。"""
        if not 1 <= max_iterations <= 3:
            raise ValueError('迭代次数必须在 1 到 3 之间')
        started = time.perf_counter()
        env = dict(env_input)
        iterations = []
        candidate = None
        result = None
        for number in range(1, max_iterations + 1):
            if number > 1 and time.perf_counter() - started >= 45:
                break
            iteration_env = dict(env)
            iteration_env['map_seed'] = int(env.get('map_seed', env.get('random_seed', 42)))
            # 地图固定，改变算法采样种子；使用独立的种子区间。
            iteration_env['random_seed'] = int(env.get('random_seed', 42)) + (number - 1) * 10000
            result = self.run(iteration_env, grid=grid, n_runs=n_runs, time_budget_s=time_budget_s, expected_algorithm=candidate)
            iterations.append({'iteration': number, 'cycle_id': result['cycle_id'], 'hypothesis': result['hypothesis'],
                               'supported': result['hypothesis_supported'], 'run_ids': result['reflection']['run_ids'],
                               'decision': result['decision']['best_algorithm']})
            if result['status'] != 'completed' or result['hypothesis_supported']:
                break
            candidate = result['decision']['best_algorithm']
            if not candidate or candidate == result['hypothesis']['expected_algorithm']:
                break
            if grid is None:
                validated = result['env_input']
                grid = MapGenerator(seed=int(env.get('random_seed', 42))).generate(validated['map_width'], validated['map_height'], float(env.get('obstacle_ratio', .15)), tuple(validated['start_point']), tuple(validated['target_point']))
        if not result:
            raise RuntimeError('时间预算不足以启动实验')
        result['iterations'] = iterations
        result['reflection']['stop_reason'] = ('假设得到本地图实验支持' if result['hypothesis_supported'] else
            '达到迭代或时间预算；结论仍需复核' if len(iterations) >= max_iterations or time.perf_counter() - started >= 45 else
            '没有可执行的下一轮修正')
        result['timings']['total_seconds'] = round(time.perf_counter() - started, 4)
        if result['timings']['total_seconds'] > 60:
            result['status'] = 'budget_exceeded'
            result['decision']['best_algorithm'] = None
            result['decision']['best_score'] = None
            result['decision']['need_human_check'] = True
            result['decision']['change_reason'] = '总耗时超过离线演示预算，暂不输出最终推荐。'
            result['hypothesis_supported'] = None
            result['reflection']['stop_reason'] = '超过离线演示时间预算，结论未完成'
        result['cycle_id'] = 'cycle_' + uuid.uuid4().hex
        result['report'] = render_report(result)
        with ExperimentDB(self.db_path) as db:
            db.save_research_cycle(result['cycle_id'], result['map_id'], result['status'], result)
        return result


def render_report(result):
    """将决策及可追溯的逐次记录导出为报告。"""
    import json
    evidence = {k: v for k, v in result.items() if k != 'report'}
    return '# 当前地图实验与选型报告\n\n' + '```json\n' + json.dumps(evidence, ensure_ascii=False, indent=2) + '\n```\n'
