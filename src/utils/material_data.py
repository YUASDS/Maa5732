# -*- coding: utf-8 -*-
"""材料刷取: 数据加载与选关规则(纯函数, 不依赖 maa/Qt)

规则见 docs/superpowers/specs/2026-09-12-material-farming-design.md 第 4/5 节。
"""
import json
import re
from typing import Optional

from src.utils.paths import asset_path

DATA_PATH = asset_path("resource", "data", "material_farm.json")
DEFAULT_PROGRESS = (2, 13, -1)  # 第13章, 关卡级进度未知
# 本期只做主线: 数字章节(系列 2) + N 系列(系列 3)
# 支线(系列 1)不进回退链: 其主线位置与切章方式未探测(spec 2.2/4.2)
SUPPORTED_SERIES = (2, 3)
# 单材料最多尝试的候选数(spec 4.2 第 4 步)
MAX_CANDIDATES = 5


def load_material_data(path: str = None) -> dict:
    """读 material_farm.json, 并把 order 归一化为元组

    JSON 里的 order 是数组, 而 [2,13] <= (2,13) 会 TypeError, 规则一律用元组。
    """
    with open(path or DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    for mat in data.get("materials", {}).values():
        for stage in mat.get("stages", []):
            stage["order"] = tuple(stage["order"])
    return data


def progress_key(text: str) -> tuple:
    """进度字符串 -> (系列, 章号, 已通关关号)

    支持: "13" / "N10" / "N7-1/6"(章节-已通关/总数) / 空(默认第13章)
    第三位 -1 表示关卡级进度未知(只按章节判定)。定义见 spec 4.1。
    """
    text = (text or "").strip()
    if not text:
        return DEFAULT_PROGRESS
    m = re.match(r"^N(\d+)(?:-(\d+)\s*/\s*\d+)?$", text)
    if m:
        return (3, int(m.group(1)), int(m.group(2)) if m.group(2) else -1)
    m = re.match(r"^(\d+)(?:-(\d+)\s*/\s*\d+)?$", text)
    if m:
        return (2, int(m.group(1)), int(m.group(2)) if m.group(2) else -1)
    return DEFAULT_PROGRESS


def available(stage_order: tuple, key: tuple) -> bool:
    """候选是否可用

    章节更早 -> 可用; 更晚 -> 不可用; 同章 -> 关卡号 <= 已通关关号(-1 表示不限)。
    """
    s_series, s_chap = stage_order[0], stage_order[1]
    k_series, k_chap, k_cleared = key
    if (s_series, s_chap) < (k_series, k_chap):
        return True
    if (s_series, s_chap) > (k_series, k_chap):
        return False
    if k_cleared < 0:
        return True
    return stage_order[4] <= k_cleared


def build_chain(stages: list) -> list:
    """按 order 倒序的回退链(仅主线候选)"""
    return sorted(
        (s for s in stages if s["order"][0] in SUPPORTED_SERIES),
        key=lambda s: s["order"],
        reverse=True,
    )


def select_stage(chain: list, key: tuple) -> Optional[dict]:
    """链上第一个可用关卡; 都不可用返回 None"""
    for stage in chain:
        if available(stage["order"], key):
            return stage
    return None


def plan(data: dict, materials: list, key: tuple) -> dict:
    """为每个材料算出首选关卡与运行中回退序列

    - stage:     链上第一个可用关卡(不可用为 None)
    - fallbacks: 首选之后**更旧**的候选(按链序), 首选被判定不可扫荡时依次尝试
    - rejected:  首选之前**更新**的候选(因进度不够被排除), 仅用于日志/预览
    """
    out = {}
    for name in materials:
        mat = data["materials"].get(name)
        if not mat:
            out[name] = {"stage": None, "fallbacks": [], "rejected": []}
            continue
        chain = build_chain(mat["stages"])
        stage = select_stage(chain, key)
        if stage is None:
            out[name] = {"stage": None, "fallbacks": [], "rejected": list(chain)}
            continue
        index = chain.index(stage)
        out[name] = {
            "stage": stage,
            "fallbacks": chain[index + 1:],
            "rejected": chain[:index],
        }
    return out
