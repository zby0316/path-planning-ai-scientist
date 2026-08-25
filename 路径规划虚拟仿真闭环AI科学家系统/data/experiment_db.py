# data/experiment_db.py — SQLite 实验数据库

import json
import os
import sqlite3
import uuid
from datetime import datetime
from typing import Optional

from config import EXPERIMENTS_DIR, HISTORICAL_RESULTS_PATH


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS maps (
    map_id TEXT PRIMARY KEY,
    source TEXT,
    map_type TEXT,
    width INTEGER,
    height INTEGER,
    obstacle_ratio REAL,
    connectivity REAL,
    topology_randomness REAL,
    dynamic_change_rate REAL,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS algorithm_runs (
    run_id TEXT PRIMARY KEY,
    map_id TEXT,
    algorithm TEXT,
    parameters TEXT,
    runtime REAL,
    path_length REAL,
    success INTEGER,
    expanded_nodes INTEGER,
    turning_points INTEGER,
    smoothness REAL,
    safety_score REAL,
    stability_score REAL,
    compute_limit TEXT,
    seed INTEGER,
    created_at TEXT,
    FOREIGN KEY (map_id) REFERENCES maps (map_id)
);

CREATE TABLE IF NOT EXISTS hypotheses (
    hypothesis_id TEXT PRIMARY KEY,
    scene_condition TEXT,
    hypothesis_text TEXT,
    generated_by TEXT,
    evidence TEXT,
    validation_status TEXT,
    created_at TEXT
);
"""

OPTIONAL_COLUMN_ALTERS = [
    "ALTER TABLE algorithm_runs ADD COLUMN compute_cost REAL DEFAULT 0.0",
    "ALTER TABLE algorithm_runs ADD COLUMN robustness REAL DEFAULT 0.0",
]


def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


class ExperimentDB:
    """实验数据库封装：3 张表的 CRUD、统计与 JSON 导入"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            os.makedirs(EXPERIMENTS_DIR, exist_ok=True)
            db_path = os.path.join(EXPERIMENTS_DIR, "experiments.sqlite")

        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        cur = self.conn.cursor()
        for stmt in SCHEMA_SQL.strip().split(";"):
            stmt = stmt.strip()
            if stmt:
                cur.execute(stmt)
        for stmt in OPTIONAL_COLUMN_ALTERS:
            try:
                cur.execute(stmt)
            except sqlite3.OperationalError:
                pass
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def insert_map(
        self,
        source: str = "",
        map_type: str = "random",
        width: int = 0,
        height: int = 0,
        obstacle_ratio: float = 0.0,
        connectivity: float = 0.0,
        topology_randomness: float = 0.0,
        dynamic_change_rate: float = 0.0,
        map_id: Optional[str] = None,
    ) -> str:
        if map_id is None:
            map_id = f"map_{uuid.uuid4().hex[:12]}"
        self.conn.execute(
            """
            INSERT OR REPLACE INTO maps
            (map_id, source, map_type, width, height, obstacle_ratio,
             connectivity, topology_randomness, dynamic_change_rate, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                map_id, source, map_type, width, height, obstacle_ratio,
                connectivity, topology_randomness, dynamic_change_rate, _now_iso(),
            ),
        )
        self.conn.commit()
        return map_id

    def insert_run(
        self,
        map_id: str,
        algorithm: str,
        runtime: float,
        path_length: float,
        success: bool,
        expanded_nodes: int = 0,
        turning_points: int = 0,
        smoothness: float = 0.0,
        safety_score: float = 0.0,
        stability_score: float = 0.0,
        compute_cost: float = 0.0,
        robustness: float = 0.0,
        parameters: Optional[dict] = None,
        compute_limit: str = "medium",
        seed: Optional[int] = None,
        run_id: Optional[str] = None,
    ) -> str:
        if run_id is None:
            run_id = f"run_{uuid.uuid4().hex[:12]}"
        params_str = json.dumps(parameters or {}, ensure_ascii=False)
        self.conn.execute(
            """
            INSERT OR REPLACE INTO algorithm_runs
            (run_id, map_id, algorithm, parameters, runtime, path_length,
             success, expanded_nodes, turning_points, smoothness, safety_score,
             stability_score, compute_limit, seed, created_at,
             compute_cost, robustness)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id, map_id, algorithm, params_str, float(runtime),
                float(path_length), int(bool(success)),
                int(expanded_nodes), int(turning_points),
                float(smoothness), float(safety_score),
                float(stability_score), compute_limit, seed, _now_iso(),
                float(compute_cost), float(robustness),
            ),
        )
        self.conn.commit()
        return run_id

    def insert_hypothesis(
        self,
        scene_condition: str,
        hypothesis_text: str,
        generated_by: str = "hypothesis_agent",
        evidence: str = "",
        validation_status: str = "pending",
        hypothesis_id: Optional[str] = None,
    ) -> str:
        if hypothesis_id is None:
            hypothesis_id = f"hyp_{uuid.uuid4().hex[:12]}"
        self.conn.execute(
            """
            INSERT OR REPLACE INTO hypotheses
            (hypothesis_id, scene_condition, hypothesis_text, generated_by,
             evidence, validation_status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                hypothesis_id, scene_condition, hypothesis_text, generated_by,
                evidence, validation_status, _now_iso(),
            ),
        )
        self.conn.commit()
        return hypothesis_id

    def query_runs_by_map(self, map_id: str) -> list:
        cur = self.conn.execute(
            "SELECT * FROM algorithm_runs WHERE map_id = ?", (map_id,)
        )
        return [dict(r) for r in cur.fetchall()]

    def query_runs_by_algorithm(self, algorithm: str) -> list:
        cur = self.conn.execute(
            "SELECT * FROM algorithm_runs WHERE algorithm = ?", (algorithm,)
        )
        return [dict(r) for r in cur.fetchall()]

    def query_runs_by_scene(
        self,
        min_obstacle: float = 0.0,
        max_obstacle: float = 1.0,
    ) -> list:
        cur = self.conn.execute(
            """
            SELECT r.*, m.obstacle_ratio
            FROM algorithm_runs r
            JOIN maps m ON r.map_id = m.map_id
            WHERE m.obstacle_ratio >= ? AND m.obstacle_ratio <= ?
            """,
            (min_obstacle, max_obstacle),
        )
        return [dict(r) for r in cur.fetchall()]

    def get_statistics(self) -> dict:
        cur = self.conn.cursor()

        total_maps = cur.execute("SELECT COUNT(*) FROM maps").fetchone()[0]
        total_runs = cur.execute("SELECT COUNT(*) FROM algorithm_runs").fetchone()[0]
        total_hypotheses = cur.execute("SELECT COUNT(*) FROM hypotheses").fetchone()[0]

        algo_stats = cur.execute(
            """
            SELECT algorithm,
                   COUNT(*) AS n,
                   AVG(runtime) AS avg_runtime,
                   AVG(path_length) AS avg_path_length,
                   AVG(success) AS avg_success,
                   AVG(smoothness) AS avg_smoothness,
                   AVG(safety_score) AS avg_safety,
                   AVG(stability_score) AS avg_stability
            FROM algorithm_runs
            GROUP BY algorithm
            """
        ).fetchall()

        algorithms = {}
        for row in algo_stats:
            algorithms[row["algorithm"]] = {
                "n_runs": row["n"],
                "avg_runtime": round(row["avg_runtime"] or 0, 4),
                "avg_path_length": round(row["avg_path_length"] or 0, 2),
                "avg_success_rate": round(row["avg_success"] or 0, 4),
                "avg_smoothness": round(row["avg_smoothness"] or 0, 4),
                "avg_safety_score": round(row["avg_safety"] or 0, 4),
                "avg_stability": round(row["avg_stability"] or 0, 4),
            }

        return {
            "db_path": self.db_path,
            "total_maps": total_maps,
            "total_runs": total_runs,
            "total_hypotheses": total_hypotheses,
            "algorithms": algorithms,
        }

    def import_from_json(self, json_filepath: str = HISTORICAL_RESULTS_PATH) -> int:
        """将 historical_results.json 导入 SQLite，返回导入条数"""
        if not os.path.exists(json_filepath):
            return 0

        with open(json_filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            return 0

        count = 0
        for record in data:
            algorithm = record.get("algorithm", "unknown")
            scene_level = record.get("scene_level", "未知")
            map_id = self.insert_map(
                source="historical_results",
                map_type="historical",
                width=100,
                height=100,
                obstacle_ratio=_scene_to_ratio(scene_level),
            )
            self.insert_run(
                map_id=map_id,
                algorithm=algorithm,
                runtime=float(record.get("avg_time", 0.0)),
                path_length=float(record.get("avg_path_length", 0.0)),
                success=bool(record.get("success_rate", 0) >= 0.5),
                expanded_nodes=0,
                turning_points=0,
                smoothness=0.0,
                safety_score=0.0,
                stability_score=float(record.get("stability_score", 0.0)),
                parameters={"scene_level": scene_level},
                compute_limit="medium",
                seed=None,
            )
            count += 1
        return count


def _scene_to_ratio(scene_level: str) -> float:
    return {
        "低复杂度": 0.10,
        "中复杂度": 0.35,
        "高复杂度": 0.65,
    }.get(scene_level, 0.30)
