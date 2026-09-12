# -*- coding: utf-8 -*-
"""材料刷取动作测试(桩): python tests/test_farm_action.py"""
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

FAILS, PASSES = [], []


def check(name, ok, detail=""):
    (PASSES if ok else FAILS).append(name)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" :: {detail}" if detail else ""))


import src.core.actions.FarmMaterial as FM  # noqa: E402
from src.core.actions.FarmMaterial import FarmMaterial  # noqa: E402

# ---------------------------------------------------------------- 参数解析
f = FarmMaterial()
p = f._load_param({
    "裂生冰晶锥checkBox": True, "结霜毒砂晶checkBox": False, "燃念赤晶checkBox": True,
    "SweepCountCombo": "5", "ProgressModeCombo": "手动", "ProgressCombo": "N10",
})
check("材料列表解析", p["materials"] == ["裂生冰晶锥", "燃念赤晶"], str(p["materials"]))
check("次数解析", p["sweep_count"] == 5, str(p["sweep_count"]))
check("进度模式解析", p["progress_mode"] == "手动")
check("手动进度解析", p["progress_manual"] == "N10")
check("空参数回退默认",
      f._load_param(None)["sweep_count"] == 3 and f._load_param(None)["materials"] == [])
check("非法次数回退 3", f._load_param({"SweepCountCombo": "abc"})["sweep_count"] == 3)
check("次数越界收敛", f._load_param({"SweepCountCombo": "99"})["sweep_count"] == 20)

payload = {"裂生冰晶锥checkBox": True, "SweepCountCombo": "4",
           "ProgressModeCombo": "手动", "ProgressCombo": "N10"}
p_str = f._load_param(json.dumps(payload, ensure_ascii=False))
check("支持 JSON 字符串(框架实际形态)",
      p_str["materials"] == ["裂生冰晶锥"] and p_str["sweep_count"] == 4
      and p_str["progress_manual"] == "N10", str(p_str))
p_dbl = f._load_param(json.dumps(json.dumps(payload, ensure_ascii=False), ensure_ascii=False))
check("支持二次编码的字符串", p_dbl["materials"] == ["裂生冰晶锥"], str(p_dbl))
check("非法字符串不抛异常", f._load_param("not-json")["materials"] == [])

# ---------------------------------------------------------------- 执行序列桩
class FakeStatus:
    succeeded = True


class FakeDetail:
    status = FakeStatus()


class FakeClick:
    """记录调用序列; fail_texts 里的 ocr_click 返回 None(驱动不可用/体力不足分支)"""

    def __init__(self, context=None):
        self.context = context
        self.calls = []
        self.fail_texts = set()
        self.count_text = "3"

    def ocr_roi(self, roi, sleep_time=None):
        self.calls.append(("ocr_roi", (roi,)))
        return [(self.count_text, 0.99, [0, 0, 1, 1])]

    def ocr(self, *args, **kwargs):
        self.calls.append(("ocr", args))
        return {}

    def __getattr__(self, name):
        def rec(*args, **kwargs):
            self.calls.append((name, args))
            if name == "ocr_click" and args and args[0] in self.fail_texts:
                return None
            return FakeDetail()
        return rec


slept = []
FM.stop_sleep = lambda s: slept.append(s)
FM.save_confg = lambda: None
FM.NAV_READY = True
FM.FarmMaterial._detect_progress = lambda self, c: "N10"
FM.FarmMaterial._load_remaining = lambda self: []
FM.FarmMaterial._switch_region = lambda self, c, s: True
FM.cfg.formatted_today = "2026-09-12"
written = {}
FM.FarmMaterial._save_remaining = lambda self, items: written.update(items=list(items))


def arg(items):
    return type("A", (), {"custom_action_param": items})


# --- 正常路径: 只有『取消』返回失败 ---
fake = FakeClick()
fake.fail_texts = {"取消"}
FM.Click = lambda context: fake
FarmMaterial().run(context=None, argv=arg({
    "裂生冰晶锥checkBox": True, "SweepCountCombo": "3",
    "ProgressModeCombo": "手动", "ProgressCombo": "N10"}))

names = [c[0] for c in fake.calls]
texts = [a[0] for n, a in fake.calls if n == "ocr_click" and a]
check("先回主页", names[0] == "check_return_home", str(names[:3]))
check("进入关卡选择(危机管理)", any(n == "click_rate" for n in names[:4]), str(names[:4]))
check("包含『连续扫荡』", "连续扫荡" in texts, str(texts[:8]))
check("包含『开始扫荡』", "开始扫荡" in texts, str(texts[:10]))
check("包含『完成』", "完成" in texts, str(texts[:10]))
check("返回主页次数 >= 1", names.count("check_return_home") >= 1, str(names.count("check_return_home")))
check("结算后等待 >= 10s", any(s >= 10 for s in slept), str(slept))
check("正常路径不写剩余列表", not written, str(written))

# --- 关卡候选回退: 链首点不到 -> 顺链下一个候选 ---
written.clear()
slept.clear()
from src.utils.material_data import load_material_data, plan, progress_key  # noqa: E402

_entry = plan(load_material_data(), ["裂生冰晶锥"], progress_key("N10"))["裂生冰晶锥"]
_head, _second = _entry["stage"]["code"], _entry["fallbacks"][0]["code"]
fake_retry = FakeClick()
fake_retry.fail_texts = {"取消", _head}          # 链首关卡编号点不到
FM.Click = lambda context: fake_retry
FarmMaterial().run(context=None, argv=arg({
    "裂生冰晶锥checkBox": True, "SweepCountCombo": "3",
    "ProgressModeCombo": "手动", "ProgressCombo": "N10"}))
tried = [a[0] for n, a in fake_retry.calls if n == "ocr_click" and a]
check(f"首选({_head})不可用时回退到次选({_second})",
      tried.count(_head) >= 1 and _second in tried, str(tried[:12]))
check("回退成功不写剩余列表", not written, str(written))

# --- 体力不足: 『取消』成功 -> 当前及后续材料写入剩余 ---
written.clear()
FM.Click = lambda context: FakeClick()
FarmMaterial().run(context=None, argv=arg({
    "裂生冰晶锥checkBox": True, "结霜毒砂晶checkBox": True, "SweepCountCombo": "3",
    "ProgressModeCombo": "手动", "ProgressCombo": "N10"}))
check("体力不足写出剩余材料(含后续)",
      written.get("items") == ["裂生冰晶锥", "结霜毒砂晶"], str(written))


# --- 停止: run 被 add_action 包了 warp_custom_stop, 不外抛, 断言副作用 ---
class StopClick(FakeClick):
    def __getattr__(self, name):
        def rec(*args, **kwargs):
            self.calls.append((name, args))
            if name == "ocr_click":
                raise FM.StopException("stop")
            return FakeDetail()
        return rec


written.clear()
FM.Click = lambda context: StopClick()
FarmMaterial().run(context=None, argv=arg({
    "裂生冰晶锥checkBox": True, "SweepCountCombo": "3",
    "ProgressModeCombo": "手动", "ProgressCombo": "N10"}))
check("停止时记录了剩余材料", written.get("items") == ["裂生冰晶锥"], str(written))

# --- 零材料: 直接跳过 ---
written.clear()
fake_empty = FakeClick()
FM.Click = lambda context: fake_empty
FarmMaterial().run(context=None, argv=arg({"SweepCountCombo": "3"}))
check("零材料不点击不记录", not fake_empty.calls and not written, str(fake_empty.calls))

# --- 未完探测: NAV_READY=False 时不点击 ---
FM.NAV_READY = False
fake_nav = FakeClick()
FM.Click = lambda context: fake_nav
FarmMaterial().run(context=None, argv=arg({
    "裂生冰晶锥checkBox": True, "ProgressModeCombo": "手动", "ProgressCombo": "N10"}))
check("未探测坐标时安全跳过", not fake_nav.calls, str(fake_nav.calls[:3]))
FM.NAV_READY = True

# --- 手动进度下不触发探测 ---
called = []
FM.FarmMaterial._detect_progress = lambda self, c: called.append(1) or "N10"
FM.Click = lambda context: FakeClick()
FarmMaterial().run(context=None, argv=arg({
    "裂生冰晶锥checkBox": True, "ProgressModeCombo": "手动", "ProgressCombo": "N10"}))
check("手动模式不探测进度", not called, str(called))

print(f"\nPASS={len(PASSES)} FAIL={len(FAILS)}")
for f_ in FAILS:
    print("  -", f_)
sys.exit(1 if FAILS else 0)
