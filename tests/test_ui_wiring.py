# -*- coding: utf-8 -*-
"""材料刷取界面接线测试(offscreen 真实 Qt): python tests/test_ui_wiring.py"""
import os
import sys

os.environ["QT_QPA_PLATFORM"] = "offscreen"
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from PySide6.QtWidgets import QApplication, QCheckBox  # noqa: E402

FAILS, PASSES = [], []


def check(name, ok, detail=""):
    (PASSES if ok else FAILS).append(name)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" :: {detail}" if detail else ""))


app = QApplication.instance() or QApplication([])

import src.utils.configs as C  # noqa: E402
from src.ui import ui_controller as UC  # noqa: E402

C.cfg.auto_run = False
C.cfg.check_update = False
UC.save_confg = lambda: None  # 不写真实配置

w = UC.MyWidget()
check("任务开关已注册", "FarmMaterial" in w.check_box_dict, str(sorted(w.check_box_dict)))
farm = w.detail_dict.get("FarmMaterial", {})
check("FarmMaterial 详细设置已注册", bool(farm), str(sorted(farm.keys())[:5]))
check("材料 checkbox 数量为 12",
      len([k for k, v in farm.items() if isinstance(v, QCheckBox)]) == 12,
      str(len([k for k, v in farm.items() if isinstance(v, QCheckBox)])))
check("次数下拉存在", "SweepCountCombo" in farm)
check("进度模式下拉存在", "ProgressModeCombo" in farm)
check("进度下拉存在", "ProgressCombo" in farm)
check("次数选项为 1..20",
      [farm["SweepCountCombo"].itemText(i) for i in range(farm["SweepCountCombo"].count())]
      == [str(i) for i in range(1, 21)])
check("进度模式选项为 自动/手动",
      [farm["ProgressModeCombo"].itemText(i) for i in range(farm["ProgressModeCombo"].count())]
      == ["自动", "手动"])
combo_chaps = [farm["ProgressCombo"].itemText(i) for i in range(farm["ProgressCombo"].count())]
check("进度选项含全部主线章节", "13" in combo_chaps and "N10" in combo_chaps and "1" in combo_chaps,
      str(combo_chaps))
check("默认选中每关 3 次", farm["SweepCountCombo"].currentText() == "3", farm["SweepCountCombo"].currentText())
check("默认选中自动模式", farm["ProgressModeCombo"].currentText() == "自动")

# 材料图标已加载(不是空图标)
mat_key = "裂生冰晶锥checkBox"
check(f"材料 checkbox 存在: {mat_key}", mat_key in farm)
check("材料图标已设置", not farm[mat_key].icon().isNull())

# 读写往返
w.check_box_dict["FarmMaterial"].setChecked(True)
farm[mat_key].setChecked(True)
farm["SweepCountCombo"].setCurrentText("5")
state = w.state_to_json()
check("state_to_json 含 FarmMaterial 详细设置", "FarmMaterial" in state[1], str(sorted(state[1].keys())))
check("勾选状态被带出", state[1]["FarmMaterial"][mat_key] is True)
check("次数被带出", state[1]["FarmMaterial"]["SweepCountCombo"] == "5")
check("开关被带出", state[0]["FarmMaterial"] is True)
w.load_from_json(state)
check("load_from_json 往返一致",
      farm["SweepCountCombo"].currentText() == "5" and farm[mat_key].isChecked())

# 决策预览
w.refresh_farm_preview()
text = w.ui.FarmMaterial_PreviewLabel.text()
check("预览显示了选定材料与关卡", "裂生冰晶锥" in text and "→" in text, text.replace("\n", " | ")[:120])
farm[mat_key].setChecked(False)
w.refresh_farm_preview()
check("无选中时预览提示未选择", w.ui.FarmMaterial_PreviewLabel.text() == "未选择材料",
      w.ui.FarmMaterial_PreviewLabel.text())

# 按钮接线
w.ui.FarmMaterialButton.click()
check("按钮切换到材料页",
      w.ui.stackedWidget.currentWidget() is w.ui.RestPage_1,
      w.ui.stackedWidget.currentWidget().objectName())

print(f"\nPASS={len(PASSES)} FAIL={len(FAILS)}")
for f in FAILS:
    print("  -", f)
sys.exit(1 if FAILS else 0)
