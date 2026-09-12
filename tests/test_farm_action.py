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
from src.utils.material_data import load_material_data, plan, progress_key  # noqa: E402

_orig_detect = FarmMaterial._detect_progress  # 保存真实实现供最后一个用例使用

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

# ---------------------------------------------------------------- 执行桩
# 主界面只放主界面元素(这样 _open_map 必须真的去点「危机管理」);
# 第一次点击后切换到"综合界面"(含所有后续步骤的文本), 便于验证后续点击序列。
MAIN_SCREEN = ["危机管理", "情绪检测", "公告", "邮箱", "狄斯", "ReN7-2"]
UNION_SCREEN = [
    "历史模式", "特别行动", "内海", "狄斯城",           # 副本界面标记
    "新城", "远邦",                                     # 旋盘标签
    "N10", "N8", "1/6", "完成前置关卡",                 # 章节节点/面板
    "N10-1", "N10-2", "任务进度1/6",                    # 关卡列表
    "编号：N10-1", "单次扫荡", "连续扫荡", "行动开始",    # 关卡详情
    "选择次数3", "设置阵容", "开始扫荡", "完成",          # 次数弹窗
]


class FakeStatus:
    succeeded = True


class FakeDetail:
    status = FakeStatus()


class FakeClick:
    """桩: 全屏 OCR 返回 screen 里的文本(带假框), 次数 ROI 返回 count_text

    点击走 click_rate(比例坐标), 由 _click_text 的精确匹配驱动 —— 测的是真实匹配逻辑。
    """

    def __init__(self, context=None):
        self.context = context
        self.calls = []
        self.main_screen = list(MAIN_SCREEN)
        self.union_screen = list(UNION_SCREEN)
        self.screen = self.main_screen
        self.count_text = "3"
        self.advanced = False

    def ocr_roi(self, roi, sleep_time=None):
        self.calls.append(("ocr_roi", (roi,)))
        if list(roi) == [0, 0, 1, 1]:
            # 假框: 同一行、x 递增(进度配对要求章节在进度文本左侧且同一行)
            return [(t, 0.99, [100 + 60 * i, 400, 50, 20])
                    for i, t in enumerate(self.screen)]
        return [(self.count_text, 0.99, [400, 430, 40, 20])]

    def click_rate(self, x, y, offset_x=5, offset_y=5):
        """第一次点击(点「危机管理」)后进入后续步骤的综合界面"""
        self.calls.append(("click_rate", (x, y)))
        if not self.advanced:
            self.advanced = True
            self.screen = self.union_screen
        return FakeDetail()

    def ocr(self, *args, **kwargs):
        self.calls.append(("ocr", args))
        return {}

    def ocr_click(self, *args, **kwargs):
        """默认视为找不到(返回 None); 体力不足用例里覆盖为成功"""
        self.calls.append(("ocr_click", args))
        return None

    def __getattr__(self, name):
        def rec(*args, **kwargs):
            self.calls.append((name, args))
            return FakeDetail()
        return rec


slept = []
FM.stop_sleep = lambda s: slept.append(s)
FM.save_confg = lambda: None
FM.FarmMaterial._detect_progress = lambda self, c: "N10"
FM.FarmMaterial._load_remaining = lambda self: []
FM.cfg.formatted_today = "2026-09-12"
written = {}
FM.FarmMaterial._save_remaining = lambda self, items: written.update(items=list(items))

clicked = []
_orig_click_text = FM.FarmMaterial._click_text


def rec_click_text(self, clicker, text):
    ok = _orig_click_text(self, clicker, text)
    clicked.append((str(text), ok))
    return ok


FM.FarmMaterial._click_text = rec_click_text


def arg(items):
    return type("A", (), {"custom_action_param": items})


MANUAL = {"SweepCountCombo": "3", "ProgressModeCombo": "手动", "ProgressCombo": "N10"}

# --- 正常路径 ---
clicked.clear()
slept.clear()
fake = FakeClick()
FM.Click = lambda context: fake
FarmMaterial().run(context=None, argv=arg(dict(MANUAL, **{"裂生冰晶锥checkBox": True})))

names = [c[0] for c in fake.calls]
ok_texts = [t for t, ok in clicked if ok]
check("先回主页", names[0] == "check_return_home", str(names[:3]))
check("点了『危机管理』", "危机管理" in ok_texts, str(ok_texts))
check("点了章节节点", "N10" in ok_texts, str(ok_texts))
check("点了关卡编号", "N10-1" in ok_texts, str(ok_texts))
check("点了『连续扫荡』", "连续扫荡" in ok_texts, str(ok_texts))
check("点了『开始扫荡』", "开始扫荡" in ok_texts, str(ok_texts))
check("点了『完成』", "完成" in ok_texts, str(ok_texts))
check("结算后等待 >= 10s", any(s >= 10 for s in slept), str(slept))
check("正常路径不写剩余列表", not written, str(written))

# --- 运行中回退: 首选关卡不可扫荡 -> 顺链下一个候选 ---
clicked.clear()
written.clear()
_entry = plan(load_material_data(), ["裂生冰晶锥"], progress_key("N10"))["裂生冰晶锥"]
_head, _second = _entry["stage"]["code"], _entry["fallbacks"][0]["code"]
attempted = []
_orig_farm_one = FM.FarmMaterial._farm_one


def fake_farm_one(self, clicker, stage):
    attempted.append(stage["code"])
    return "unavailable" if stage["code"] == _head else "ok"


FM.FarmMaterial._farm_one = fake_farm_one
FM.Click = lambda context: FakeClick()
FarmMaterial().run(context=None, argv=arg(dict(MANUAL, **{"裂生冰晶锥checkBox": True})))
check(f"首选({_head})不可用时回退到次选({_second})",
      attempted[:2] == [_head, _second], str(attempted[:3]))
check("回退成功不写剩余列表", not written, str(written))
FM.FarmMaterial._farm_one = _orig_farm_one

# --- 体力不足: 弹窗里出现『取消』 -> 当前及后续材料写入剩余 ---
class CancelClick(FakeClick):
    def ocr_click(self, *args, **kwargs):
        self.calls.append(("ocr_click", args))
        return FakeDetail() if args and args[0] == "取消" else None


written.clear()
FM.Click = lambda context: CancelClick()
FarmMaterial().run(context=None, argv=arg(dict(
    MANUAL, **{"裂生冰晶锥checkBox": True, "结霜毒砂晶checkBox": True})))
check("体力不足写出剩余材料(含后续)",
      written.get("items") == ["裂生冰晶锥", "结霜毒砂晶"], str(written))

# --- 停止: run 被 add_action 包了 warp_custom_stop, 不外抛, 断言副作用 ---
class StopClick(FakeClick):
    def click_rate(self, *args, **kwargs):
        raise FM.StopException("stop")


written.clear()
FM.Click = lambda context: StopClick()
FarmMaterial().run(context=None, argv=arg(dict(MANUAL, **{"裂生冰晶锥checkBox": True})))
check("停止时记录了剩余材料", written.get("items") == ["裂生冰晶锥"], str(written))

# --- 零材料: 直接跳过 ---
written.clear()
fake_empty = FakeClick()
FM.Click = lambda context: fake_empty
FarmMaterial().run(context=None, argv=arg({"SweepCountCombo": "3"}))
check("零材料不点击不记录", not fake_empty.calls and not written, str(fake_empty.calls))

# --- 未探测坐标(NAV_READY=False) 时不点击 ---
FM.NAV_READY = False
fake_nav = FakeClick()
FM.Click = lambda context: fake_nav
FarmMaterial().run(context=None, argv=arg(dict(
    {"ProgressModeCombo": "手动", "ProgressCombo": "N10"}, **{"裂生冰晶锥checkBox": True})))
check("未探测坐标时安全跳过", not fake_nav.calls, str(fake_nav.calls[:3]))
FM.NAV_READY = True

# --- 手动进度下不触发探测 ---
called = []
FM.FarmMaterial._detect_progress = lambda self, c: called.append(1) or "N10"
FM.Click = lambda context: FakeClick()
FarmMaterial().run(context=None, argv=arg(dict(MANUAL, **{"裂生冰晶锥checkBox": True})))
check("手动模式不探测进度", not called, str(called))

# --- 进度探测: 地图上「章节文本 + x/y」配对(用真实实现) ---
FM.FarmMaterial._detect_progress = _orig_detect
detect_fake = FakeClick()
detect_fake.union_screen = ["N7", "1/6", "历史模式", "特别行动", "狄斯城"]
FM.Click = lambda context: detect_fake
detected = FarmMaterial()._detect_progress(detect_fake)
check("进度配对解析(N7 + 1/6 -> N7-1/6)", detected == "N7-1/6", str(detected))

detect_fake2 = FakeClick()
detect_fake2.union_screen = ["N7", "历史模式", "特别行动", "狄斯城"]
check("只有章节没有进度 -> 空", FarmMaterial()._detect_progress(detect_fake2) == "")

print(f"\nPASS={len(PASSES)} FAIL={len(FAILS)}")
for f_ in FAILS:
    print("  -", f_)
sys.exit(1 if FAILS else 0)
