# -*- coding: utf-8 -*-
"""材料刷取数据自检: python tests/test_material_data.py"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "assets", "resource", "data", "material_farm.json")
ICON_DIR = os.path.join(BASE, "assets", "resource", "image", "material")
ZERO_ORDER = [0, 0, 0, "", 0]   # spec §4.1 "其它/无法解析"
# spec §4.1 表格的字面值: 不经过正则的独立 oracle, 防止"用同一套正则自证"
SPEC_4_1 = {
    "N3-A3": [3, 3, 1, "A", 3],
    "13-18": [2, 13, 0, "", 18],
    "SdN2-2": [1, 2, 0, "", 2],
    "Sd-1104": [1, 11, 0, "", 4],
}
FAILS, PASSES = [], []


def check(name, ok, detail=""):
    (PASSES if ok else FAILS).append(name)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" :: {detail}" if detail else ""))


def expected_order(code):
    """spec 4.1 的独立实现, 与生成脚本交叉验证(只依赖编号形态, 不依赖类型字段)"""
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
    return list(ZERO_ORDER)


if not os.path.exists(DATA):
    check("数据文件存在", False, DATA)
else:
    data = json.load(open(DATA, encoding="utf-8"))
    mats = data["materials"]
    check("材料数量为 12", len(mats) == 12, str(len(mats)))
    check("全部为紫阶", all(m["rarity"] == "紫" for m in mats.values()))
    check("每个材料都有图标字段与候选章节", all(m.get("icon") and m.get("candidate_chapters") for m in mats.values()))
    check("materials 不含 spec §3.2 未列的 effect 字段", not any("effect" in m for m in mats.values()))

    icon_field_bad, no_icon, no_stage = [], [], []
    order_bad, zero_bad, unsorted, chapter_bad = [], [], [], []
    for name, m in mats.items():
        if m.get("icon") != f"material/{name}.png":
            icon_field_bad.append(f"{name}: {m.get('icon')!r}")
        if not os.path.exists(os.path.join(ICON_DIR, f"{name}.png")):
            no_icon.append(name)
        if not m["stages"]:
            no_stage.append(name)
        cands = set(m.get("candidate_chapters") or [])
        orders = [list(s["order"]) for s in m["stages"]]
        if any(tuple(orders[i]) < tuple(orders[i + 1]) for i in range(len(orders) - 1)):
            unsorted.append(name)
        for s in m["stages"]:
            if list(s["order"]) != expected_order(s["code"]):
                order_bad.append(f"{s['code']}={s['order']}")
            if list(s["order"]) == ZERO_ORDER:
                zero_bad.append(s["code"])
            if s["chapter"] not in cands:
                chapter_bad.append(f"{name}/{s['code']}: {s['chapter']}")

    check("icon 字段为 material/<材料名>.png", not icon_field_bad, str(icon_field_bad[:3]))
    check("图标文件齐全", not no_icon, str(no_icon))
    expected_icons = {f"{name}.png" for name in mats}
    actual_icons = ({f for f in os.listdir(ICON_DIR) if f.lower().endswith(".png")}
                    if os.path.isdir(ICON_DIR) else set())
    check("图标目录内容恰为 12 个目标图标(无过期图标)", actual_icons == expected_icons,
          f"多余={sorted(actual_icons - expected_icons)} 缺失={sorted(expected_icons - actual_icons)}")
    check("每个材料都有候选关卡", not no_stage, str(no_stage))
    check("order 与编号逐一一致(独立实现交叉验证)", not order_bad,
          f"{len(order_bad)} 条不符, 例: {order_bad[:5]}")
    check("没有无法解析的编号(order 不得为 [0,0,0,\"\",0])", not zero_bad,
          f"{len(zero_bad)} 条: {sorted(set(zero_bad))[:5]}")
    check("每个材料的 stages 按 order 倒序", not unsorted, str(unsorted))
    check("每个 stage 的 chapter 都在该材料 candidate_chapters 内", not chapter_bad,
          f"{len(chapter_bad)} 条, 例: {chapter_bad[:5]}")

    by_code = {s["code"]: list(s["order"]) for m in mats.values() for s in m["stages"]}
    for code, want in SPEC_4_1.items():
        check(f"数据中的 order 等于 spec 4.1 字面值: {code} -> {want}",
              by_code.get(code) == want, f"数据中为 {by_code.get(code)}")
        check(f"独立实现与 spec 4.1 字面值一致: {code}",
              expected_order(code) == want, f"{expected_order(code)}")

    nulls = [s["code"] for m in mats.values() for s in m["stages"] if s["stamina"] is None]
    check("体力为空的情况与数据一致(仅 N8-7)", sorted(nulls) == ["N8-7"], str(nulls))

    check("chapters 含全部主线数字章节 1..13",
          data["chapters"]["主线"] == list(range(1, 14)), str(data["chapters"]["主线"]))
    check("chapters 含 N 系列实际章号",
          data["chapters"]["主线N"] == [1, 2, 3, 4, 7, 8, 9, 10], str(data["chapters"]["主线N"]))

print(f"\nPASS={len(PASSES)} FAIL={len(FAILS)}")
for f in FAILS:
    print("  -", f)
sys.exit(1 if FAILS else 0)
