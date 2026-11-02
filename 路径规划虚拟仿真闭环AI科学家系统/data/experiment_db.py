# data/experiment_db.py — SQLite 实验数据库

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
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

CREATE TABLE IF NOT EXISTS research_cycles (
    cycle_id TEXT PRIMARY KEY,
    map_id TEXT,
    status TEXT NOT NULL,
    result_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS map_grids (
    map_id TEXT PRIMARY KEY,
    height INTEGER NOT NULL,
    width INTEGER NOT NULL,
    cells BLOB NOT NULL,
    FOREIGN KEY (map_id) REFERENCES maps (map_id)
);

CREATE TABLE IF NOT EXISTS robustness_raw (
    raw_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    map_id TEXT NOT NULL,
    algorithm TEXT NOT NULL,
    frame_index INTEGER NOT NULL,
    perturb_index INTEGER NOT NULL,
    details_json TEXT NOT NULL,
    FOREIGN KEY (run_id) REFERENCES algorithm_runs (run_id)
);

CREATE TABLE IF NOT EXISTS run_raw (
    raw_id TEXT PRIMARY KEY,
    run_id TEXT,
    map_id TEXT,
    algorithm TEXT,
    frame_index INTEGER DEFAULT 0,
    repeat_index INTEGER,
    seed INTEGER,
    time_budget_s REAL,
    runtime_s REAL,
    reported_success INTEGER,
    valid_success INTEGER,
    invalid_reason TEXT,
    path_nodes INTEGER,
    geometric_length REAL,
    turning_points INTEGER,
    safety_score REAL,
    nodes_expanded INTEGER,
    timeout INTEGER,
    created_at TEXT,
    FOREIGN KEY (map_id) REFERENCES maps (map_id)
);
"""

OPTIONAL_COLUMN_ALTERS = [
    "ALTER TABLE algorithm_runs ADD COLUMN compute_cost REAL DEFAULT 0.0",
    "ALTER TABLE algorithm_runs ADD COLUMN robustness REAL DEFAULT 0.0",
    "ALTER TABLE algorithm_runs ADD COLUMN success_rate REAL DEFAULT -1.0",
    "ALTER TABLE algorithm_runs ADD COLUMN reported_success_rate REAL DEFAULT -1.0",
    "ALTER TABLE algorithm_runs ADD COLUMN timeout_rate REAL DEFAULT -1.0",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds")


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

    def save_research_cycle(self, cycle_id: str, map_id: str, status: str, result: dict) -> None:
        self.conn.execute(
            "INSERT INTO research_cycles (cycle_id, map_id, status, result_json, created_at) VALUES (?, ?, ?, ?, ?)",
            (cycle_id, map_id, status, json.dumps(result, ensure_ascii=False), _now_iso()),
        )
        self.conn.commit()

    def get_research_cycle(self, cycle_id: str) -> Optional[dict]:
        row = self.conn.execute("SELECT result_json FROM research_cycles WHERE cycle_id = ?", (cycle_id,)).fetchone()
        return json.loads(row["result_json"]) if row else None

    def save_map_grid(self, map_id: str, grid) -> None:
        import numpy as np
        grid = np.asarray(grid, dtype=np.uint8)
        self.conn.execute("INSERT INTO map_grids (map_id, height, width, cells) VALUES (?, ?, ?, ?)",
                          (map_id, grid.shape[0], grid.shape[1], grid.tobytes()))
        self.conn.commit()

    def get_map_grid(self, map_id: str):
        import numpy as np
        row = self.conn.execute("SELECT height, width, cells FROM map_grids WHERE map_id = ?", (map_id,)).fetchone()
        return np.frombuffer(row['cells'], dtype=np.uint8).reshape(row['height'], row['width']).copy() if row else None

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
        success_rate: float = -1.0,
        reported_success_rate: float = -1.0,
        timeout_rate: float = -1.0,
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
             compute_cost, robustness, success_rate, reported_success_rate, timeout_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id, map_id, algorithm, params_str, float(runtime),
                float(path_length), int(bool(success)),
                int(expanded_nodes), int(turning_points),
                float(smoothness), float(safety_score),
                float(stability_score), compute_limit, seed, _now_iso(),
                float(compute_cost), float(robustness),
                float(success_rate), float(reported_success_rate), float(timeout_rate),
            ),
        )
        self.conn.commit()
        return run_id

    def record_benchmark_run(
        self,
        map_id: str,
        algorithm: str,
        metrics: dict,
        parameters: Optional[dict] = None,
        compute_limit: str = "medium",
        seed: Optional[int] = None,
    ) -> str:
        """统一落库：聚合行（algorithm_runs）+ 逐次明细行（run_raw）。

        聚合值中的 success_rate / reported_success_rate / timeout_rate / avg_time
        从 run_raw 明细重算，保证库内自洽、可追溯。
        metrics 为 evaluate_algorithm 的返回 dict（含 runs 列表）。
        """
        runs = metrics.get("runs") or []
        n_runs = len(runs)

        if n_runs > 0:
            valid_rate = sum(1 for r in runs if r.get("valid_success")) / n_runs
            reported_rate = sum(1 for r in runs if r.get("reported_success")) / n_runs
            timeout_rate = sum(1 for r in runs if r.get("timeout")) / n_runs
            avg_time = float(sum(r.get("runtime_s", 0.0) for r in runs) / n_runs)
        else:
            valid_rate = float(metrics.get("success_rate", 0.0))
            reported_rate = float(metrics.get("reported_success_rate", valid_rate))
            timeout_rate = float(metrics.get("timeout_rate", 0.0))
            avg_time = float(metrics.get("avg_time", 0.0))

        run_id = self.insert_run(
            map_id=map_id,
            algorithm=algorithm,
            runtime=avg_time,
            path_length=metrics.get("avg_path_length", 0.0),
            success=bool(valid_rate >= 0.5),
            expanded_nodes=metrics.get("expanded_nodes", 0),
            turning_points=metrics.get("turning_points", 0),
            smoothness=metrics.get("smoothness", 0.0),
            safety_score=metrics.get("safety_score", 0.0),
            stability_score=metrics.get("stability_score", 0.0),
            compute_cost=metrics.get("compute_cost", 0.0),
            robustness=metrics.get("robustness", 0.0),
            parameters=parameters,
            compute_limit=compute_limit,
            seed=seed,
            success_rate=round(valid_rate, 4),
            reported_success_rate=round(reported_rate, 4),
            timeout_rate=round(timeout_rate, 4),
        )

        now = _now_iso()
        for r in runs:
            self.conn.execute(
                """
                INSERT INTO run_raw
                (raw_id, run_id, map_id, algorithm, frame_index, repeat_index, seed,
                 time_budget_s, runtime_s, reported_success, valid_success,
                 invalid_reason, path_nodes, geometric_length, turning_points,
                 safety_score, nodes_expanded, timeout, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"raw_{uuid.uuid4().hex[:12]}",
                    run_id, map_id, algorithm,
                    int(r.get("frame_index", 0)),
                    int(r.get("run_index", 0)),
                    int(r.get("seed", 0)) if r.get("seed") is not None else None,
                    float(r.get("time_budget_s", 0.0) or 0.0),
                    float(r.get("runtime_s", 0.0)),
                    int(bool(r.get("reported_success"))),
                    int(bool(r.get("valid_success"))),
                    r.get("invalid_reason", "") or "",
                    int(r.get("path_nodes", 0) or 0),
                    float(r["geometric_length"]) if r.get("geometric_length") is not None else None,
                    int(r.get("turning_points", 0) or 0),
                    float(r.get("safety_score", 0.0) or 0.0),
                    int(r.get("nodes_expanded", 0) or 0),
                    int(bool(r.get("timeout"))),
                    now,
                ),
            )
        for r in metrics.get('robustness_runs', []):
            self.conn.execute(
                "INSERT INTO robustness_raw (raw_id, run_id, map_id, algorithm, frame_index, perturb_index, details_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (f"rob_{uuid.uuid4().hex[:12]}", run_id, map_id, algorithm,
                 int(r.get('frame_index', 0)), int(r.get('perturb_index', 0)),
                 json.dumps(r, ensure_ascii=False)),
            )
        self.conn.commit()
        return run_id

    def query_raw_runs(
        self,
        map_id: Optional[str] = None,
        algorithm: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> list:
        sql = "SELECT * FROM run_raw WHERE 1=1"
        args = []
        if map_id is not None:
            sql += " AND map_id = ?"
            args.append(map_id)
        if algorithm is not None:
            sql += " AND algorithm = ?"
            args.append(algorithm)
        if run_id is not None:
            sql += " AND run_id = ?"
            args.append(run_id)
        sql += " ORDER BY created_at, repeat_index"
        cur = self.conn.execute(sql, args)
        return [dict(r) for r in cur.fetchall()]

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
        total_raw_runs = cur.execute("SELECT COUNT(*) FROM run_raw").fetchone()[0]

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
            "total_raw_runs": total_raw_runs,
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
