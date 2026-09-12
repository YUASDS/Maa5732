# -*- coding: utf-8 -*-
"""材料刷取数据自检: python tests/test_material_data.py"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "assets", "resource", "data", "material_farm.json")
ICON_DIR = os.path.join(BASE, "assets", "resource", "image", "material")
FAILS, PASSES = [], []


def check(name, ok, detail=""):
    (PASSES if ok else FAILS).append(name)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" :: {detail}" if detail else ""))


def expected_order(code):
    """spec 4.1 的独立实现, 与生成脚本交叉验证(只依赖编号前缀, 不依赖类型字段)"""
    m = re.match(r"^N(\d+)-([A-Za-z]?)(\d+)$", code)
    if m:
        return [3, int(m.group(1)), 1 if m.group(2) else 0, m.group(2), int(m.group(3))]
    m = re.match(r"^(\d+)-(\d+)$", code)
    if m:
        return [2, int(m.group(1)), 0, "", int(m.group(2))]
    m = re.match(r"^SdN(\d+)-(\d+)$", code)
    if m:
        return [1, int(m.group(1)), 0, "", int(m.group(2))]
    m = re.match(r"^Sd-(\d\d)(\d\d)$", code)
    if m:
        return [1, int(m.group(1)), 0, "", int(m.group(2))]
    return [0, 0, 0, "", 0]


if not os.path.exists(DATA):
    check("数据文件存在", False, DATA)
else:
    data = json.load(open(DATA, encoding="utf-8"))
    mats = data["materials"]
    check("材料数量为 12", len(mats) == 12, str(len(mats)))
    check("全部为紫阶", all(m["rarity"] == "紫" for m in mats.values()))
    check("每个材料都有图标字段与候选章节", all(m.get("icon") and m.get("candidate_chapters") for m in mats.values()))

    order_bad, no_icon, no_stage = [], [], []
    for name, m in mats.items():
        icon = os.path.join(ICON_DIR, os.path.basename(m["icon"]))
        if not os.path.exists(icon):
            no_icon.append(name)
        if not m["stages"]:
            no_stage.append(name)
        for s in m["stages"]:
            if list(s["order"]) != expected_order(s["code"]):
                order_bad.append(f"{s['code']}={s['order']}")
    check("图标文件齐全", not no_icon, str(no_icon))
    check("每个材料都有候选关卡", not no_stage, str(no_stage))
    check("order 与编号逐一一致(独立实现交叉验证)", not order_bad,
          f"{len(order_bad)} 条不符, 例: {order_bad[:5]}")

    nulls = [s["code"] for m in mats.values() for s in m["stages"] if s["stamina"] is None]
    check("体力为空的情况与数据一致(仅 N8-7)", nulls == ["N8-7"], str(nulls))

    check("chapters 含全部主线数字章节 1..13",
          data["chapters"]["主线"] == list(range(1, 14)), str(data["chapters"]["主线"]))
    check("chapters 含 N 系列实际章号",
          data["chapters"]["主线N"] == [1, 2, 3, 4, 7, 8, 9, 10], str(data["chapters"]["主线N"]))

print(f"\nPASS={len(PASSES)} FAIL={len(FAILS)}")
for f in FAILS:
    print("  -", f)
sys.exit(1 if FAILS else 0)
