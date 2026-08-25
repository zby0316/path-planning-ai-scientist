from __future__ import annotations

import time
import uuid
import threading
from contextlib import asynccontextmanager
from typing import Any, Dict
from collections import defaultdict

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from api.schemas import (
    EnvInputRequest,
    DecisionResponse,
    HypothesisResponse,
    ReportResponse,
    ExperimentRequest,
    ExperimentResponse,
)
from utils.logging_config import setup_logging

setup_logging()

rate_limit_store: Dict[str, list] = defaultdict(list)
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 30

experiment_store: Dict[str, Dict[str, Any]] = {}
experiment_lock = threading.Lock()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="路径规划算法自适应选型 AI Scientist API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    rate_limit_store[client_ip] = [
        t for t in rate_limit_store[client_ip] if now - t < RATE_LIMIT_WINDOW
    ]
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_MAX:
        raise HTTPException(status_code=429, detail="Too many requests")
    rate_limit_store[client_ip].append(now)
    response = await call_next(request)
    return response


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(request: EnvInputRequest):
    try:
        from agents.orchestrator_agent import OrchestratorAgent
        orchestrator = OrchestratorAgent()
        env_input = request.model_dump()
        state = orchestrator.run(env_input)
        result = state.to_dict()
        result["env_input"] = env_input
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(exc)}")


@app.post("/experiment", status_code=202)
async def run_experiment(request: ExperimentRequest):
    run_id = f"exp_{uuid.uuid4().hex[:12]}"
    experiment_data = {
        "run_id": run_id,
        "status": "running",
        "progress": 0.0,
        "results": None,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "request": request.model_dump(),
    }
    with experiment_lock:
        experiment_store[run_id] = experiment_data

    def _run_background():
        try:
            from evaluation.experiment_runner import ExperimentRunner
            map_params = request.map_params
            scale = (
                map_params.get("width", 50),
                map_params.get("height", 50),
            )
            dynamic_change_rate = float(
                map_params.get("dynamic_change_rate", request.dynamic_change_rate) or 0.0
            )
            dynamic_steps = int(map_params.get("dynamic_steps", 5) or 5)
            runner = ExperimentRunner()
            results = runner.run_quick(
                n_maps_per_complexity=min(request.n_runs, 5),
                scale=scale,
                compute_limit=request.compute_limit,
                n_runs_per_algo=max(1, request.n_runs // 2),
                dynamic_change_rate=dynamic_change_rate,
                dynamic_steps=dynamic_steps,
            )
            filtered_results = [
                r for r in results
                if r.get("algorithm") in request.algorithms
            ] if request.algorithms else results
            with experiment_lock:
                experiment_store[run_id]["status"] = "completed"
                experiment_store[run_id]["progress"] = 1.0
                experiment_store[run_id]["results"] = filtered_results
        except Exception as exc:
            with experiment_lock:
                experiment_store[run_id]["status"] = "failed"
                experiment_store[run_id]["results"] = {"error": str(exc)}

    thread = threading.Thread(target=_run_background, daemon=True)
    thread.start()

    return ExperimentResponse(
        run_id=run_id,
        status="running",
        progress=0.0,
        results=None,
        created_at=experiment_data["created_at"],
    )


@app.get("/experiment/{run_id}")
async def get_experiment(run_id: str):
    with experiment_lock:
        data = experiment_store.get(run_id)
    if data is None:
        raise HTTPException(status_code=404, detail=f"实验 {run_id} 未找到")
    return {
        "run_id": data["run_id"],
        "status": data["status"],
        "progress": data["progress"],
        "results": data["results"],
        "created_at": data["created_at"],
    }


@app.get("/report/{run_id}", response_class=PlainTextResponse)
async def get_report(run_id: str):
    with experiment_lock:
        data = experiment_store.get(run_id)
    if data is None:
        raise HTTPException(status_code=404, detail=f"报告 {run_id} 未找到")

    try:
        from agents.research_state import ResearchState
        from reports.report_generator import ReportGenerator
        results = data.get("results") or []
        request_data = data.get("request", {})
        env_input = dict(request_data.get("map_params", {}) or {})
        env_input.setdefault("dynamic_change_rate", request_data.get("dynamic_change_rate", 0.0))
        env_input.setdefault("compute_limit", request_data.get("compute_limit", "medium"))
        if isinstance(results, list):
            best = max(results, key=lambda r: r.get("success_rate", 0), default={})
            experiment_results = results
        elif isinstance(results, dict):
            best = results
            experiment_results = [results]
        else:
            best = {}
            experiment_results = []
        state = ResearchState(
            env_input=env_input,
            decision={"best_algorithm": best.get("algorithm", best.get("best_algorithm", "N/A"))},
            experiment_results=experiment_results,
        )
        report_gen = ReportGenerator(state)
        report = report_gen.generate()
        return report
    except Exception:
        import json as _json
        results = data.get("results") or {}
        report_lines = [
            f"# 实验报告 - {run_id}",
            f"",
            f"**状态**: {data.get('status', 'N/A')}",
            f"**创建时间**: {data.get('created_at', 'N/A')}",
            f"",
            f"## 结果",
            f"```json",
            _json.dumps(results, ensure_ascii=False, indent=2),
            f"```",
        ]
        return "\n".join(report_lines)
