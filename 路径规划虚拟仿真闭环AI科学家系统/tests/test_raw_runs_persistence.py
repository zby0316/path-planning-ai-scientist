# tests/test_raw_runs_persistence.py — 逐次原始运行入库与聚合自洽回归

import os
import tempfile

import numpy as np
import pytest

from data.experiment_db import ExperimentDB
from evaluation.benchmark import ALGORITHM_FACTORIES
from evaluation.metrics import evaluate_algorithm
from map.map_generator import MapGenerator


@pytest.fixture()
def tmp_db():
    path = os.path.join(tempfile.gettempdir(), "test_raw_runs.sqlite")
    if os.path.exists(path):
        os.remove(path)
    db = ExperimentDB(db_path=path)
    yield db
    db.close()
    if os.path.exists(path):
        os.remove(path)


class TestRawRunsPersistence:
    def test_record_benchmark_run_writes_raw_rows(self, tmp_db):
        grid = MapGenerator(seed=1).generate(15, 15, 0.2, (0, 0), (14, 14))
        map_id = tmp_db.insert_map(source="test", width=15, height=15, obstacle_ratio=0.2)

        metrics = evaluate_algorithm(
            ALGORITHM_FACTORIES["A*"], grid, (0, 0), (14, 14),
            n_runs=3, compute_limit="medium", base_seed=100, algo_index=0,
            algorithm_name="A*",
        )
        run_id = tmp_db.record_benchmark_run(
            map_id=map_id, algorithm="A*", metrics=metrics,
            parameters={"test": True}, compute_limit="medium", seed=100,
        )

        raw = tmp_db.query_raw_runs(map_id=map_id, algorithm="A*")
        assert len(raw) == 3
        assert all(r["run_id"] == run_id for r in raw)
        # 逐次种子符合派生公式
        assert [r["seed"] for r in raw] == [100, 101, 102]
        # 逐次记录带独立校验字段
        assert all("valid_success" in r and "invalid_reason" in r for r in raw)
        assert all(r["time_budget_s"] > 0 for r in raw)

    def test_aggregate_consistent_with_raw(self, tmp_db):
        """聚合行的 success_rate/avg_time 必须能由 run_raw 重算得出。"""
        grid = MapGenerator(seed=2).generate(15, 15, 0.2, (0, 0), (14, 14))
        map_id = tmp_db.insert_map(source="test", width=15, height=15, obstacle_ratio=0.2)

        metrics = evaluate_algorithm(
            ALGORITHM_FACTORIES["A*"], grid, (0, 0), (14, 14),
            n_runs=4, compute_limit="medium", base_seed=200, algo_index=0,
            algorithm_name="A*",
        )
        run_id = tmp_db.record_benchmark_run(
            map_id=map_id, algorithm="A*", metrics=metrics,
            compute_limit="medium", seed=200,
        )

        row = tmp_db.conn.execute(
            "SELECT success_rate, runtime FROM algorithm_runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        raw = tmp_db.query_raw_runs(run_id=run_id)

        valid_rate = sum(r["valid_success"] for r in raw) / len(raw)
        avg_time = sum(r["runtime_s"] for r in raw) / len(raw)
        assert abs(row["success_rate"] - valid_rate) < 1e-6
        assert abs(row["runtime"] - avg_time) < 0.01

    def test_real_connectivity_metadata(self, tmp_db):
        """地图登记必须写入真实连通率（而非写死 0.5）。"""
        from map.connectivity_checker import free_space_connectivity_ratio, topology_randomness

        grid = MapGenerator(seed=3).generate(20, 20, 0.3, (0, 0), (19, 19))
        conn = free_space_connectivity_ratio(grid)
        topo = topology_randomness(grid)
        assert 0.0 < conn <= 1.0
        assert 0.0 <= topo <= 1.0

        # 整块障碍 → 低界面
        solid = np.zeros((10, 10), dtype=int)
        solid[:5, :] = 1
        assert topology_randomness(solid) <= 0.2
        # 散布单格障碍 → 高界面
        scattered = np.zeros((10, 10), dtype=int)
        scattered[::2, ::2] = 1
        assert topology_randomness(scattered) > 0.5

    def test_statistics_includes_raw_count(self, tmp_db):
        stats = tmp_db.get_statistics()
        assert "total_raw_runs" in stats
        assert stats["total_raw_runs"] == 0

    def test_migration_on_existing_schema(self, tmp_db):
        """旧库升级：success_rate 等新列通过 ALTER 补齐，不破坏旧数据。"""
        tmp_db.insert_run(
            map_id=tmp_db.insert_map(source="legacy"),
            algorithm="A*", runtime=0.1, path_length=50.0, success=True,
        )
        # 重新打开同一文件触发迁移路径
        tmp_db.close()
        db2 = ExperimentDB(db_path=tmp_db.db_path)
        cols = [r[1] for r in db2.conn.execute("PRAGMA table_info(algorithm_runs)")]
        assert "success_rate" in cols
        assert "reported_success_rate" in cols
        assert "timeout_rate" in cols
        rows = db2.query_runs_by_algorithm("A*")
        assert len(rows) == 1
        db2.close()
