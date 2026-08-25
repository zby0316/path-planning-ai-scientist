# agents/map_analysis_agent.py — 地图结构分析智能体
"""从栅格地图中提取障碍物聚类、瓶颈通道、空间分布熵等结构特征（Phase 4）。

设计目标
--------
- 与 ``EnvironmentAgent`` 解耦：``EnvironmentAgent`` 负责"复杂度等级"判定，
  ``MapAnalysisAgent`` 负责"地图结构特征"提取。
- ``extract_features`` / ``analyze`` 都能从栅格中计算 4 个新指标（提示词 4-2）：
  ``cluster_count`` / ``bottleneck_count`` / ``entropy`` / ``distance_to_target``。
- 缺失底层依赖（如 ``scipy``）时优雅降级为 0，不抛错。
- 与 ``ResearchState`` 深度集成：``analyze(state)`` 接收并返回
  ``ResearchState``，结果合并到 ``state.map_features``。
"""

from __future__ import annotations

import logging
import math
from collections import deque
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from agents.research_state import ResearchState
from map.map_analyzer import MapAnalyzer
from map.map_parser import MapParser

logger = logging.getLogger(__name__)

try:
    from scipy.ndimage import label as _scipy_label  # type: ignore

    _HAS_SCIPY = True
except Exception as exc:  # pragma: no cover - 离线场景
    logger.warning("scipy.ndimage 导入失败: %s", exc)
    _scipy_label = None
    _HAS_SCIPY = False


def _label_4conn(mask: np.ndarray) -> Tuple[int, np.ndarray]:
    """4 邻接连通区域标记。

    Parameters
    ----------
    mask : np.ndarray of bool
        ``True`` 表示被标记的像素。

    Returns
    -------
    (num_features, labels) : (int, np.ndarray)
        ``num_features`` 为连通区域数；``labels`` 形状同 ``mask``，
        每个像素为所属区域编号（0 表示背景）。
    """
    h, w = mask.shape
    labels = np.zeros((h, w), dtype=np.int32)
    if not mask.any():
        return 0, labels

    current = 0
    for i in range(h):
        for j in range(w):
            if mask[i, j] and labels[i, j] == 0:
                current += 1
                queue = deque([(i, j)])
                labels[i, j] = current
                while queue:
                    y, x = queue.popleft()
                    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        ny, nx = y + dy, x + dx
                        if (
                            0 <= ny < h
                            and 0 <= nx < w
                            and mask[ny, nx]
                            and labels[ny, nx] == 0
                        ):
                            labels[ny, nx] = current
                            queue.append((ny, nx))
    return current, labels


def _label_4conn_fast(mask: np.ndarray) -> Tuple[int, np.ndarray]:
    """优先用 scipy 的快速实现，否则回退到自实现 BFS。"""
    if _HAS_SCIPY and _scipy_label is not None:
        # scipy 的 label 默认就是 4 邻接
        structure = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.int8)
        labeled, num = _scipy_label(mask, structure=structure)
        return int(num), labeled.astype(np.int32)
    return _label_4conn(mask)


def _shannon_entropy(probs: np.ndarray) -> float:
    """给定概率分布（不必归一化），返回 Shannon 熵。"""
    if probs is None or len(probs) == 0:
        return 0.0
    total = float(probs.sum())
    if total <= 0:
        return 0.0
    p = probs / total
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


class MapAnalysisAgent:
    """地图结构分析智能体（Phase 4）。"""

    def __init__(self) -> None:
        self._analyzer = MapAnalyzer()

    # ------------------------------------------------------------------ #
    # 栅格层特征
    # ------------------------------------------------------------------ #
    def analyze_grid(self, grid: np.ndarray) -> Dict[str, Any]:
        """计算 4 个结构特征：``cluster_count`` / ``largest_free_ratio`` /
        ``bottleneck_count`` / ``entropy``。"""
        if not isinstance(grid, np.ndarray):
            grid = np.asarray(grid)
        if grid.ndim != 2 or grid.size == 0:
            return {
                "cluster_count": 0,
                "largest_free_ratio": 0.0,
                "bottleneck_count": 0,
                "entropy": 0.0,
            }

        # 障碍物掩码（值为 1 视为障碍）
        obstacle_mask = (grid == 1)
        free_mask = (grid == 0)

        # 1. 障碍物聚类数
        num_clusters, _ = _label_4conn_fast(obstacle_mask)
        cluster_count = int(num_clusters)

        # 2. 最大可通行区域占比
        _, free_labels = _label_4conn_fast(free_mask)
        if free_labels.max() > 0:
            sizes = np.bincount(free_labels.ravel())[1:]  # 跳过背景 0
            largest_free = int(sizes.max()) if len(sizes) > 0 else 0
        else:
            largest_free = 0
        largest_free_ratio = round(largest_free / float(grid.size), 4)

        # 3. 瓶颈通道数（宽度 < 3 的必经通道近似）
        bottleneck_count = self._estimate_bottlenecks(grid)

        # 4. 障碍物空间分布熵（按行 + 列分别统计 1 的占比后求 Shannon 熵）
        row_ratio = obstacle_mask.sum(axis=1) / max(1, grid.shape[1])
        col_ratio = obstacle_mask.sum(axis=0) / max(1, grid.shape[0])
        combined = np.concatenate([row_ratio, col_ratio]).astype(float)
        entropy = round(_shannon_entropy(combined), 4)

        return {
            "cluster_count": cluster_count,
            "largest_free_ratio": largest_free_ratio,
            "bottleneck_count": int(bottleneck_count),
            "entropy": entropy,
        }

    @staticmethod
    def _estimate_bottlenecks(grid: np.ndarray) -> int:
        """启发式估计"瓶颈通道"数量。

        简化策略：寻找满足以下条件的"窄通道"行/列——
        1) 在自由空间（值为 0）连续段中，长度恰好为 1 或 2 个像素；
        2) 且其上下（行方向）或左右（列方向）均为障碍物（值为 1）。

        返回估算的瓶颈数量上限。
        """
        h, w = grid.shape
        if h < 3 or w < 3:
            return 0

        count = 0
        # 行方向扫描
        for i in range(1, h - 1):
            j = 0
            while j < w:
                if grid[i, j] == 0:
                    k = j
                    while k < w and grid[i, k] == 0:
                        k += 1
                    seg_len = k - j
                    # 段长 < 3 且上下均为障碍
                    if 0 < seg_len < 3:
                        upper = grid[i - 1, j:k]
                        lower = grid[i + 1, j:k]
                        if upper.size > 0 and lower.size > 0:
                            if (upper == 1).all() and (lower == 1).all():
                                count += 1
                    j = k
                else:
                    j += 1

        # 列方向扫描
        for j in range(1, w - 1):
            i = 0
            while i < h:
                if grid[i, j] == 0:
                    k = i
                    while k < h and grid[k, j] == 0:
                        k += 1
                    seg_len = k - i
                    if 0 < seg_len < 3:
                        left = grid[i:k, j - 1]
                        right = grid[i:k, j + 1]
                        if left.size > 0 and right.size > 0:
                            if (left == 1).all() and (right == 1).all():
                                count += 1
                    i = k
                else:
                    i += 1
        return count

    # ------------------------------------------------------------------ #
    # 整合：栅格 + MapAnalyzer.analyze + 距离
    # ------------------------------------------------------------------ #
    def extract_features(
        self,
        grid: np.ndarray,
        start: Tuple[int, int],
        target: Tuple[int, int],
        connectivity: float = 0.5,
        topology_randomness: float = 0.5,
        dynamic_change_rate: float = 0.0,
    ) -> Dict[str, Any]:
        """整合 ``MapAnalyzer.analyze`` 与 ``analyze_grid`` 的全部字段。"""
        if not isinstance(grid, np.ndarray):
            grid = np.asarray(grid)
        base = self._analyzer.analyze(
            grid=grid,
            start=start,
            target=target,
            connectivity=connectivity,
            topology_randomness=topology_randomness,
            dynamic_change_rate=dynamic_change_rate,
        )
        struct = self.analyze_grid(grid)
        base.update(struct)
        return base

    # ------------------------------------------------------------------ #
    # ResearchState 集成
    # ------------------------------------------------------------------ #
    def analyze(self, state: ResearchState) -> ResearchState:
        """从 ``state`` 中取栅格，写入 ``state.map_features``，返回 ``state``。"""
        if state.metadata is None:
            state.metadata = {}
        state.metadata.setdefault("errors", [])

        grid = self._resolve_grid(state)

        if grid is None:
            # 没有栅格时仍尝试基于 env_input 写入占位特征
            env = state.env_input or {}
            start = tuple(env.get("start_point", [0, 0]))
            target = tuple(env.get("target_point", [env.get("map_width", 0) - 1, env.get("map_height", 0) - 1]))
            distance = abs(int(start[0]) - int(target[0])) + abs(int(start[1]) - int(target[1]))
            state.map_features = {
                "scene_level": env.get("scene_level", "N/A"),
                "obstacle_ratio": env.get("obstacle_ratio", 0.0),
                "start": list(start),
                "target": list(target),
                "free_space_ratio": round(1.0 - float(env.get("obstacle_ratio", 0.0)), 4),
                "total_cells": int(env.get("map_width", 0)) * int(env.get("map_height", 0)),
                "cluster_count": 0,
                "bottleneck_count": 0,
                "entropy": 0.0,
                "distance_to_target": distance,
            }
            return state

        env = state.env_input or {}
        start = tuple(env.get("start_point", [0, 0]))
        target = tuple(env.get("target_point", [grid.shape[0] - 1, grid.shape[1] - 1]))

        try:
            features = self.extract_features(
                grid=grid,
                start=start,
                target=target,
                connectivity=float(env.get("connectivity", 0.5)),
                topology_randomness=float(env.get("topology_randomness", 0.5)),
                dynamic_change_rate=float(env.get("dynamic_change_rate", 0.0)),
            )
        except Exception as exc:  # 任何底层异常都不应中断 orchestrator
            logger.error("MapAnalysisAgent.extract_features 失败: %s", exc, exc_info=True)
            state.metadata["errors"].append(f"MapAnalysisAgent.analyze: {exc}")
            # 占位
            features = {
                "cluster_count": 0,
                "bottleneck_count": 0,
                "entropy": 0.0,
                "distance_to_target": abs(int(start[0]) - int(target[0]))
                + abs(int(start[1]) - int(target[1])),
            }

        # 与既有 map_features 合并（保留 grid 等原始字段）
        merged = dict(state.map_features or {})
        merged.update(features)
        merged["grid"] = grid
        state.map_features = merged
        return state

    # ------------------------------------------------------------------ #
    def _resolve_grid(self, state: ResearchState) -> Optional[np.ndarray]:
        """优先 ``state.map_features["grid"]``，否则尝试 ``env_input["map_filepath"]``。"""
        existing = (state.map_features or {}).get("grid")
        if existing is not None:
            try:
                return np.asarray(existing)
            except Exception as exc:
                logger.warning("MapAnalysisAgent._resolve_grid np.asarray 转换失败: %s", exc)
                pass
        map_filepath = (state.env_input or {}).get("map_filepath")
        if map_filepath:
            try:
                parsed = MapParser().parse(map_filepath)
                grid = parsed.get("grid")
                if grid is not None:
                    return np.asarray(grid)
            except Exception as exc:
                if state.metadata is not None:
                    logger.error("MapAnalysisAgent 解析 %s 失败: %s", map_filepath, exc, exc_info=True)
                    state.metadata.setdefault("errors", []).append(
                        f"MapAnalysisAgent 解析 {map_filepath} 失败: {exc}"
                    )
        return None


__all__ = ["MapAnalysisAgent"]
