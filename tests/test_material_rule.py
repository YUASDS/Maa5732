# -*- coding: utf-8 -*-
"""选关规则测试: python tests/test_material_rule.py"""
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from src.utils.material_data import (  # noqa: E402
    build_chain,
    load_material_data,
    plan,
    progress_key,
)

FAILS, PASSES = [], []


def check(name, ok, detail=""):
    (PASSES if ok else FAILS).append(name)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" :: {detail}" if detail else ""))


data = load_material_data()

# ---- 进度字符串 -> 键 ----
check("进度 13 -> (2,13,-1)", progress_key("13") == (2, 13, -1), str(progress_key("13")))
check("进度 N10 -> (3,10,-1)", progress_key("N10") == (3, 10, -1), str(progress_key("N10")))
check("进度 N7-1/6 -> (3,7,1)", progress_key("N7-1/6") == (3, 7, 1), str(progress_key("N7-1/6")))
check("进度 13-4/18 -> (2,13,4)", progress_key("13-4/18") == (2, 13, 4), str(progress_key("13-4/18")))
check("空进度回退默认", progress_key("") == (2, 13, -1), str(progress_key("")))
check("非法进度回退默认", progress_key("abc") == (2, 13, -1), str(progress_key("abc")))

# ---- 默认进度(2,13,-1): 12 个材料全部落 13-x ----
expected_13 = {
    "裂生冰晶锥": "13-8", "异化尖刺骨片": "13-18", "结霜毒砂晶": "13-15",
    "衰变暮辉晶": "13-12", "异化真红囊胞": "13-14", "沉雾泪晶": "13-11",
    "异化棘状角": "13-13", "异化暗凝胶": "13-9", "繁盛曲铜晶": "13-2",
    "异化拟怪腕足": "13-4", "异化诡影鞘翅": "13-16", "燃念赤晶": "13-17",
}
plans = plan(data, list(expected_13), progress_key("13"))
for mat, want in expected_13.items():
    got = plans[mat]["stage"]["code"] if plans[mat]["stage"] else None
    check(f"默认进度选关 {mat}", got == want, f"期望 {want} 实际 {got}")
check("材料数量为 12", len(data["materials"]) == 12, str(len(data["materials"])))

# ---- 全进度 N10: 9 个走 N10, 3 个走 N9 ----
plans = plan(data, list(expected_13), progress_key("N10"))
n10 = sorted(m for m, p in plans.items() if p["stage"] and p["stage"]["code"].startswith("N10"))
n9 = sorted(m for m, p in plans.items() if p["stage"] and p["stage"]["code"].startswith("N9"))
check("全进度: 9 个走 N10", len(n10) == 9, str(n10))
check("全进度: 3 个走 N9", len(n9) == 3, str(n9))
check("全进度: 裂生冰晶锥 -> N10-1",
      plans["裂生冰晶锥"]["stage"]["code"] == "N10-1", str(plans["裂生冰晶锥"]["stage"]))

# ---- 关卡级进度: 只通了 N10-1 时 N10-4 不可用, 顺链回退 ----
plans = plan(data, ["衰变暮辉晶"], progress_key("N10-1/9"))
got = plans["衰变暮辉晶"]["stage"]["code"]
check("关卡级进度触发回退(不选 N10-4)", got != "N10-4", f"实际 {got}")
check("关卡级进度回退到 N9-1", got == "N9-1", f"实际 {got}")

# ---- 进度不足且无主线候选可用 -> 跳过 ----
# 异化尖刺骨片的候选全是主线(无支线), 进度 5 时全部不可用
plans = plan(data, ["异化尖刺骨片"], progress_key("5"))
check("进度不足且无支线候选时跳过",
      plans["异化尖刺骨片"]["stage"] is None, str(plans["异化尖刺骨片"]))

# ---- 链序: 同章内带字母子关排在无字母关号之前(降序) ----
chain = [s["code"] for s in build_chain(data["materials"]["异化暗凝胶"]["stages"])]
check("链首为 N10-8", chain[0] == "N10-8", chain[0])
check("同章内 N3-A2 在 N3-6 之前", chain.index("N3-A2") < chain.index("N3-6"), str(chain))

synth = [
    {"code": "N3-5", "order": (3, 3, 0, "", 5)},
    {"code": "N3-0", "order": (3, 3, 0, "", 0)},
    {"code": "N3-A1", "order": (3, 3, 1, "A", 1)},
    {"code": "N4-0", "order": (3, 4, 0, "", 0)},
]
s_chain = [s["code"] for s in build_chain(synth)]
check("合成链序 N4-0 > N3-A1 > N3-5 > N3-0",
      s_chain == ["N4-0", "N3-A1", "N3-5", "N3-0"], str(s_chain))

chain2 = [s["code"] for s in build_chain(data["materials"]["裂生冰晶锥"]["stages"])]
check("链中只有主线候选(支线本期不支持)",
      all(not c.startswith("Sd") for c in chain2), str(chain2))

# ---- order 归一化为元组 ----
check("order 已是元组",
      all(isinstance(s["order"], tuple) for m in data["materials"].values() for s in m["stages"]))

# ---- 回退序列语义: fallbacks 往更旧走, rejected 是更新的(仅日志用) ----
plans = plan(data, ["衰变暮辉晶"], progress_key("N10-1/9"))
entry = plans["衰变暮辉晶"]
check("首选之后的 fallback 更旧", entry["fallbacks"][0]["order"] < entry["stage"]["order"],
      f'{entry["stage"]["code"]} -> {entry["fallbacks"][0]["code"]}')
check("被排除的 rejected 更新", all(s["order"] > entry["stage"]["order"] for s in entry["rejected"]),
      str([s["code"] for s in entry["rejected"]]))
plans = plan(data, ["裂生冰晶锥"], progress_key("N10"))
check("全进度下无可排除项", plans["裂生冰晶锥"]["rejected"] == [],
      str([s["code"] for s in plans["裂生冰晶锥"]["rejected"]]))
check("全进度下 fallback 非空", len(plans["裂生冰晶锥"]["fallbacks"]) > 0)

print(f"\nPASS={len(PASSES)} FAIL={len(FAILS)}")
for f in FAILS:
    print("  -", f)
sys.exit(1 if FAILS else 0)
