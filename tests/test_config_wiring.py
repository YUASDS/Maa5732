# -*- coding: utf-8 -*-
"""配置与管线接线测试: python tests/test_config_wiring.py"""
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

FAILS, PASSES = [], []


def check(name, ok, detail=""):
    (PASSES if ok else FAILS).append(name)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" :: {detail}" if detail else ""))


import src.utils.configs as C  # noqa: E402

check("DEFAULT_SETTINGS[0] 有 FarmMaterial 且默认 False",
      C.DEFAULT_SETTINGS[0].get("FarmMaterial") is False,
      str(C.DEFAULT_SETTINGS[0].get("FarmMaterial")))
check("DEFAULT_SETTINGS[1] 有 FarmMaterial 默认块",
      C.DEFAULT_SETTINGS[1].get("FarmMaterial", {}).get("SweepCountCombo") == "3",
      str(C.DEFAULT_SETTINGS[1].get("FarmMaterial")))
check("DEFAULT_CONFIG 有 main_progress", "main_progress" in C.DEFAULT_CONFIG)
check("DEFAULT_CONFIG 有 material_remaining", "material_remaining" in C.DEFAULT_CONFIG)
check("cfg 暴露 main_progress", isinstance(C.cfg.main_progress, str), repr(C.cfg.main_progress))
check("cfg 暴露 material_remaining", isinstance(C.cfg.material_remaining, dict))
check("PIPELINE_ORDER 含 FarmMaterial 末节点",
      C.PIPELINE_ORDER[-1][1] == "FarmMaterial", str(C.PIPELINE_ORDER[-1]))
check("上一节点 next 指向新节点",
      C.PIPELINE_ORDER[-2][2] == "11", str(C.PIPELINE_ORDER[-2]))

from src.utils.parse import json2pipline  # noqa: E402

toggles = {k: False for k in C.DEFAULT_SETTINGS[0]}
details = {k: dict(v) for k, v in C.DEFAULT_SETTINGS[1].items()}
toggles["FarmMaterial"] = True
node = json2pipline([toggles, details]).get("11")
check("开关打开时节点为 FarmMaterial",
      bool(node) and node.get("custom_action") == "FarmMaterial", str(node))
toggles["FarmMaterial"] = False
node = json2pipline([toggles, details]).get("11")
check("开关关闭时节点为 Nothing",
      bool(node) and node.get("custom_action") == "Nothing", str(node))
toggles["FarmMaterial"] = True
node = json2pipline([toggles, details]).get("11")
check("节点参数含界面原始 detail 键",
      "SweepCountCombo" in (node.get("custom_action_param") or {}), str(node.get("custom_action_param")))

import src.core.actions  # noqa: E402,F401
from src.core.TaskerManager import TASKER_MANAGER  # noqa: E402

check("FarmMaterial 已注册为自定义动作", "FarmMaterial" in TASKER_MANAGER.custon_action,
      str(sorted(TASKER_MANAGER.custon_action)))

print(f"\nPASS={len(PASSES)} FAIL={len(FAILS)}")
for f in FAILS:
    print("  -", f)
sys.exit(1 if FAILS else 0)
