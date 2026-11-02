import numpy as np
import pytest

from agents.application_service import ApplicationService


class StubBenchmark:
    def run(self, grid, start, target, n_runs, **kwargs):
        records = []
        for i, name in enumerate(['A*', 'ACO', 'PSO', 'SA', '混合优化算法']):
            success = i == 1
            records.append({'algorithm': name, 'avg_time': 0.1, 'avg_path_length': 5,
                            'success_rate': float(success), 'stability_score': 1,
                            'smoothness': 0, 'safety_score': 1, 'expanded_nodes': 1,
                            'compute_cost': 0, 'robustness': float(success),
                            'runs': [{'run_index': j, 'seed': j, 'valid_success': success,
                                      'reported_success': success, 'runtime_s': .1} for j in range(n_runs)]})
        return records


def test_current_results_determine_decision_and_are_traceable(tmp_path):
    service = ApplicationService(str(tmp_path / 'runs.sqlite'), StubBenchmark())
    result = service.run({'map_width': 4, 'map_height': 4, 'compute_limit': 'medium'}, np.zeros((4, 4)))
    assert result['decision']['best_algorithm'] == 'ACO'
    assert result['prior_ranking']
    assert all(r['run_id'] for r in result['experiment_results'])
    assert result['map_id'] in result['report']


def test_invalid_or_disconnected_map_stops_before_decision(tmp_path):
    service = ApplicationService(str(tmp_path / 'runs.sqlite'), StubBenchmark())
    grid = np.zeros((4, 4)); grid[1, :] = 1
    with pytest.raises(ValueError, match='不连通'):
        service.run({'map_width': 4, 'map_height': 4}, grid)
    with pytest.raises(ValueError, match='越界'):
        service.run({'map_width': 4, 'map_height': 4, 'start_point': [-1, 0]}, grid)


def test_no_valid_path_has_no_final_recommendation(tmp_path):
    class NoSuccess(StubBenchmark):
        def run(self, *args, **kwargs):
            results = super().run(*args, **kwargs)
            for r in results:
                for run in r['runs']:
                    run['valid_success'] = False
            return results
    result = ApplicationService(str(tmp_path / 'runs.sqlite'), NoSuccess()).run(
        {'map_width': 4, 'map_height': 4}, np.zeros((4, 4)))
    assert result['status'] == 'insufficient_evidence'
    assert result['decision']['best_algorithm'] is None
    assert result['hypothesis_supported'] is None


def test_dynamic_results_preserve_frames_and_persist_cycle(tmp_path):
    from data.experiment_db import ExperimentDB
    class DynamicBenchmark(StubBenchmark):
        def run_dynamic_sequence(self, grids, start, target, n_runs, **kwargs):
            records = self.run(grids[0], start, target, n_runs, **kwargs)
            for record in records:
                original = record['runs']
                record['runs'] = [dict(run, frame_index=frame) for frame in range(len(grids)) for run in original]
            return records
    db_path = str(tmp_path / 'dynamic.sqlite')
    result = ApplicationService(db_path, DynamicBenchmark()).run_cycle(
        {'map_width': 4, 'map_height': 4, 'dynamic_change_rate': .1, 'dynamic_steps': 2},
        np.zeros((4, 4), dtype=np.int8))
    repeated = ApplicationService(db_path, DynamicBenchmark()).run_cycle(
        {'map_width': 4, 'map_height': 4, 'dynamic_change_rate': .1, 'dynamic_steps': 2},
        np.zeros((4, 4), dtype=np.int8))
    assert result['dynamic_steps'] == 2
    assert result['frame_sha256'] == repeated['frame_sha256']
    with ExperimentDB(db_path) as db:
        assert db.get_research_cycle(result['cycle_id'])['decision'] == result['decision']
        assert np.array_equal(db.get_map_grid(result['map_id']), np.zeros((4, 4)))
        assert {r['frame_index'] for r in db.query_raw_runs(map_id=result['map_id'])} == {0, 1}


def test_falsified_hypothesis_revises_candidate_and_seed(monkeypatch):
    service = ApplicationService()
    calls = []
    def fake_run(env, grid=None, n_runs=3, time_budget_s=1, expected_algorithm=None):
        calls.append((env['random_seed'], expected_algorithm))
        first = len(calls) == 1
        return {'cycle_id': str(len(calls)), 'map_id': 'map', 'status': 'completed',
                'hypothesis': {'expected_algorithm': expected_algorithm or 'A*'},
                'hypothesis_supported': not first,
                'decision': {'best_algorithm': 'ACO', 'need_human_check': False},
                'reflection': {'run_ids': ['run']}, 'timings': {}, 'report': ''}
    monkeypatch.setattr(service, 'run', fake_run)
    class MemoryDB:
        def __init__(self, *args): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def save_research_cycle(self, *args): pass
    monkeypatch.setattr('agents.application_service.ExperimentDB', MemoryDB)
    result = service.run_cycle({'random_seed': 42}, grid=np.zeros((2, 2)), max_iterations=3)
    assert calls == [(42, None), (10042, 'ACO')]
    assert len(result['iterations']) == 2
    assert result['reflection']['stop_reason'] == '假设得到本地图实验支持'


def test_feedback_and_preference_are_saved(tmp_path):
    from data.experiment_db import ExperimentDB
    db_path = str(tmp_path / 'feedback.sqlite')
    service = ApplicationService(db_path, StubBenchmark())
    env = {'map_width': 4, 'map_height': 4, 'human_feedback': '更重视速度',
           'optimization_preference': '耗时优先', 'previous_cycle_id': 'previous'}
    result = service.run_cycle(env, grid=np.zeros((4, 4)))
    assert result['weights']['time'] > .25
    with ExperimentDB(db_path) as db:
        saved = db.get_research_cycle(result['cycle_id'])
    assert saved['human_feedback'] == '更重视速度'
    assert saved['previous_cycle_id'] == 'previous'
    assert result['cycle_id'] in result['report']


def test_preference_changes_ranking_when_time_and_distance_conflict(tmp_path, monkeypatch):
    class TradeoffBenchmark(StubBenchmark):
        def run(self, *args, **kwargs):
            records = super().run(*args, **kwargs)
            for index, record in enumerate(records):
                record['avg_time'] = 0.0 if index == 0 else 1.0
                record['avg_path_length'] = 100.0 if index == 0 else 1.0
                for run in record['runs']:
                    run['valid_success'] = run['reported_success'] = index < 2
                record['success_rate'] = float(index < 2)
            return records
    monkeypatch.setattr('evaluation.scoring.load_range_dict',
                        lambda *a, **k: ({'time': (0, 1), 'path_length': (1, 100)}, 'test'))
    service = ApplicationService(str(tmp_path / 'tradeoff.sqlite'), TradeoffBenchmark())
    env = {'map_width': 4, 'map_height': 4, 'compute_limit': 'high'}
    fast = service.run_cycle({**env, 'optimization_preference': '耗时优先'}, np.zeros((4, 4)))
    short = service.run_cycle({**env, 'optimization_preference': '路径最短'}, np.zeros((4, 4)))
    assert fast['decision']['best_algorithm'] == 'A*'
    assert short['decision']['best_algorithm'] == 'ACO'


def test_api_and_legacy_pipeline_use_same_service(monkeypatch):
    import asyncio
    from api.schemas import EnvInputRequest
    from api.server import analyze
    from agents.pipeline import ScientificDiscoveryPipeline
    calls = []
    result = {'env_input': {}, 'prior_ranking': [], 'decision': {'ranking': []},
              'hypothesis': {}, 'experiment_results': [], 'reflection': {}, 'report': 'report',
              'status': 'completed', 'cycle_id': 'cycle', 'iterations': [],
              'hypothesis_supported': True, 'degraded': [], 'timings': {}}
    def fake_run(self, env, **kwargs):
        calls.append((env, kwargs))
        return result.copy()
    monkeypatch.setattr(ApplicationService, 'run_cycle', fake_run)
    request = EnvInputRequest()
    api_result = asyncio.run(analyze(request))
    pipeline_result = ScientificDiscoveryPipeline().run_full_cycle(request.model_dump(exclude={'grid', 'max_iterations'}), max_iterations=1)
    assert api_result['decision'] == pipeline_result.decision
    assert calls[0][1]['max_iterations'] == calls[1][1]['max_iterations'] == 1
    assert calls[0][0]['start_point'] is None


def test_parameter_suggestions_match_algorithm_constructors():
    from agents.parameter_agent import ParameterAgent
    from algorithms.astar import AStar
    from algorithms.aco import AntColony
    from algorithms.pso import ParticleSwarm
    from algorithms.sa import SimulatedAnnealing
    from algorithms.hybrid import HybridAlgorithm
    classes = {'A*': AStar, 'ACO': AntColony, 'PSO': ParticleSwarm,
               'SA': SimulatedAnnealing, '混合优化算法': HybridAlgorithm}
    for name, cls in classes.items():
        cls(**ParameterAgent().recommend({'compute_limit': 'medium'}, {'best_algorithm': name}))


def test_experiment_api_uses_unified_service_and_returns_its_report(monkeypatch):
    import asyncio
    import threading
    from api.schemas import ExperimentRequest
    from api.server import run_experiment, get_experiment, get_report
    called = threading.Event()
    seen = {}
    def fake_run(self, env, **kwargs):
        seen.update(env=env, options=kwargs)
        called.set()
        return {'status': 'completed', 'report': 'actual report', 'cycle_id': 'cycle'}
    monkeypatch.setattr(ApplicationService, 'run_cycle', fake_run)
    request = ExperimentRequest(algorithms=['A*'], n_runs=7, map_params={'width': 30, 'height': 30, 'obstacle_ratio': .1})
    created = asyncio.run(run_experiment(request))
    assert called.wait(2)
    # The worker sets results immediately after the fake returns.
    import time
    for _ in range(100):
        outcome = asyncio.run(get_experiment(created.run_id))
        if outcome['status'] != 'running':
            break
        time.sleep(.01)
    assert outcome['status'] == 'completed'
    assert seen['options']['n_runs'] == 7
    assert asyncio.run(get_report(created.run_id)) == 'actual report'


def test_robustness_perturbations_are_recorded(tmp_path):
    from algorithms.astar import AStar
    from data.experiment_db import ExperimentDB
    from evaluation.metrics import evaluate_algorithm
    grid = np.zeros((4, 4), dtype=np.uint8)
    metrics = evaluate_algorithm(lambda seed, time_budget_s: AStar(time_budget_s=time_budget_s),
                                 grid, (0, 0), (3, 3), n_runs=1, base_seed=42,
                                 time_budget_s=1, algorithm_name='A*')
    assert len(metrics['robustness_runs']) == 3
    with ExperimentDB(str(tmp_path / 'robustness.sqlite')) as db:
        map_id = db.insert_map(width=4, height=4)
        run_id = db.record_benchmark_run(map_id, 'A*', metrics)
        rows = db.conn.execute('SELECT details_json FROM robustness_raw WHERE run_id = ?', (run_id,)).fetchall()
    assert len(rows) == 3
    assert 'perturbation_seed' in rows[0]['details_json']
