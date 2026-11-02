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
from starlette.concurrency import run_in_threadpool

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
        from agents.application_service import ApplicationService
        env = request.model_dump()
        grid = env.pop('grid')
        max_iterations = env.pop('max_iterations')
        return await run_in_threadpool(ApplicationService().run_cycle, env, grid=grid, max_iterations=max_iterations)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(exc)}")


@app.post("/experiment", status_code=202)
async def run_experiment(request: ExperimentRequest):
    from config import ALLOWED_ALGORITHMS
    if any(name not in ALLOWED_ALGORITHMS for name in request.algorithms):
        raise HTTPException(status_code=422, detail="算法不在白名单中")
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
            from agents.application_service import ApplicationService
            params = dict(request.map_params or {})
            env = {
                "map_width": params.get("width", 30),
                "map_height": params.get("height", 30),
                "obstacle_ratio": params.get("obstacle_ratio", 0.1),
                "random_seed": params.get("random_seed", 42),
                "start_point": params.get("start_point"),
                "target_point": params.get("target_point"),
                "compute_limit": request.compute_limit,
                "dynamic_change_rate": params.get("dynamic_change_rate", request.dynamic_change_rate),
                "dynamic_steps": params.get("dynamic_steps", 2),
                "optimization_preference": params.get("optimization_preference", "平衡模式"),
            }
            result = ApplicationService().run_cycle(env, grid=params.get('grid'), n_runs=request.n_runs,
                                                    max_iterations=int(params.get('max_iterations', 1)))
            result["requested_algorithms"] = request.algorithms
            with experiment_lock:
                experiment_store[run_id]["status"] = result["status"]
                experiment_store[run_id]["progress"] = 1.0
                experiment_store[run_id]["results"] = result
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
        from data.experiment_db import ExperimentDB
        with ExperimentDB() as db:
            saved = db.get_research_cycle(run_id)
        if saved and saved.get('report'):
            return saved['report']
        raise HTTPException(status_code=404, detail=f"报告 {run_id} 未找到")

    if data.get("status") == "running":
        raise HTTPException(status_code=409, detail="实验尚未完成")
    result = data.get("results")
    if isinstance(result, dict) and result.get("report"):
        return result["report"]

    raise HTTPException(status_code=409, detail=f"实验未产生报告：{result}")
