# 导入sys
import sys
from typing import Union
from loguru import logger
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QCheckBox, QComboBox
from PySide6.QtCore import QObject, Signal

from src.ui.ui import Ui_Form
from src.utils.configs import cfg, save_confg
from src.core.ThreadManager import TaskerThread


class MySignal(QObject):
    button = Signal(QPushButton, str)


# 继承QWidget类,以获取其属性和方法
class MyWidget(QWidget):
    order = {}
    state = 0
    widget_button: list[QPushButton] = []
    check_box_dict: dict[str, QCheckBox] = {}
    detail_dict: dict[str, dict[str, Union[QCheckBox, QComboBox]]] = {}

    def __init__(self):
        super().__init__()
        self.tasker_thread = TaskerThread(self.change_running_state)
        self.tasker_thread.daemon = True
        self.tasker_thread.start()
        self.signal = MySignal()
        self.signal.button.connect(self.print_gui)

        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.widget_button.append(self.ui.GuildButton)
        self.widget_button.append(self.ui.RaidButton)
        self.widget_button.append(self.ui.StartButton)
        self.widget_button.append(self.ui.FriendsButton)
        self.widget_button.append(self.ui.PurchaseButton)
        self.widget_button.append(self.ui.SupervisionButton)
        for button in self.widget_button:
            button.clicked.connect(self.buttonClick)
        self.ui.LinkStartButton.clicked.connect(self.start)
        self.ui.SlectAllButton.clicked.connect(self.select_all)
        self.ui.ClearAllButton.clicked.connect(self.clear_all)
        # nothing 不进行注册

        self.add_check_box(self.ui.GuildcheckBox)
        self.add_check_box(self.ui.RaidcheckBox)
        self.add_check_box(self.ui.StartToHomeActioncheckBox)
        self.add_check_box(self.ui.FriendscheckBox)
        self.add_check_box(self.ui.PurchasecheckBox)
        self.add_check_box(self.ui.SupervisioncheckBox)
        self.add_check_box(self.ui.ConstructioncheckBox)
        self.add_check_box(self.ui.BureaucheckBox)
        self.add_check_box(self.ui.GetMailcheckBox)

        self.add_detail_box(self.ui.Purchase_ActivityShopcheckBox)
        self.add_detail_box(self.ui.Purchase_FreeShopcheckBox)
        self.add_detail_box(self.ui.Purchase_FriendShopcheckBox)
        self.add_detail_box(self.ui.Friends_AutoLikecheckBox)
        self.add_detail_box(self.ui.Friends_FriendPointcheckBox)
        self.add_detail_box(self.ui.Raid_RaidDarkcheckBox)
        self.add_detail_box(self.ui.Raid_RaidFightcheckBox)
        self.add_detail_box(self.ui.Raid_RaidRivercheckBox)

        self.add_detail_box(self.ui.Guild_GuildCombo)
        self.add_detail_box(self.ui.Raid_ResourceCombo)
        self.add_detail_box(self.ui.Supervision_RewardCombo)
        self.init_combo()
        self.load_from_json(cfg.settings)

    def add_check_box(self, check_box: QCheckBox):
        check_box.clicked.connect(self.checkBox)
        self.check_box_dict[check_box.objectName().replace("checkBox", "")] = check_box

    def add_detail_box(self, obj: Union[QCheckBox, QComboBox]):
        action_name = obj.objectName().split("_")[0]
        action_setting = obj.objectName().split("_")[1]
        if action_name not in self.detail_dict:
            self.detail_dict[action_name] = {}
        self.detail_dict[action_name][action_setting] = obj

    def init_combo(self):

        self.ui.Guild_GuildCombo.addItems(["狄斯币", "异方晶"])
        self.ui.Raid_ResourceCombo.addItems(
            [
                "狄斯币",
                "狂乱精粹",
                "技能模组",
                "异能源质",
                "诡秘源质",
                "坚韧源质",
                "狂暴源质",
                "精准源质",
                "启迪源质",
            ]
        )
        self.ui.Supervision_RewardCombo.addItems(["体力", "监察徽印"])

    def checkBox(self):
        box = self.sender()
        boxName = box.objectName()

    def select_all(self):
        for checkBox in self.check_box_dict.values():
            checkBox.setChecked(True)

    def clear_all(self):
        for checkBox in self.check_box_dict.values():
            checkBox.setChecked(False)

    def buttonClick(self):
        self.state_to_json()
        btn = self.sender()
        btnName = btn.objectName()
        if btnName == "RaidButton":
            self.ui.stackedWidget.setCurrentWidget(self.ui.Raid)
        if btnName == "GuildButton":
            self.ui.stackedWidget.setCurrentWidget(self.ui.Guild)
        if btnName == "StartButton":
            self.ui.stackedWidget.setCurrentWidget(self.ui.StartToHomeAction)
        if btnName == "FriendsButton":
            self.ui.stackedWidget.setCurrentWidget(self.ui.Friends)
        if btnName == "PurchaseButton":
            self.ui.stackedWidget.setCurrentWidget(self.ui.Purchase)
        if btnName == "SupervisionButton":
            self.ui.stackedWidget.setCurrentWidget(self.ui.Supervision)
        if btnName == "SlectAllButton":
            self.ui.stackedWidget.setCurrentWidget(self.ui.Supervision)
        if btnName == "ClearAllButton":
            self.ui.stackedWidget.setCurrentWidget(self.ui.Supervision)

    def print_gui(self, obj: QObject, msg: str):
        if isinstance(obj, QPushButton):
            obj.setText(msg)

    def change_running_state(self):
        if self.state == 0:
            self.signal.button.emit(self.ui.LinkStartButton, "Stop")
            self.state = 1
        else:
            self.signal.button.emit(self.ui.LinkStartButton, "Link Start ! ")
            self.state = 0

    def start(self):
        if self.state == 0:
            self.change_running_state()
            json_data = self.state_to_json()
            self.tasker_thread.add_task(self.state_to_json())
            cfg.settings = json_data
            save_confg()
        else:
            # self.change_running_state()
            self.tasker_thread.cancle_task()

    def load_from_json(self, data: list[dict]):
        for key, value in data[0].items():
            self.check_box_dict[key].setChecked(value)
        for key, value in data[1].items():
            if key in self.detail_dict:
                for inner_key, inner_value in value.items():
                    if inner_key in self.detail_dict[key]:
                        qobj = self.detail_dict[key][inner_key]
                        if isinstance(qobj, QCheckBox):
                            qobj.setChecked(inner_value)
                        else:
                            qobj.setCurrentText(inner_value)

    def state_to_json(self):
        detail_part = {key: {} for key in self.detail_dict.keys()}
        first_part = {
            name: obj.isChecked() for name, obj in self.check_box_dict.items()
        }
        for key, value in self.detail_dict.items():
            for inner_key, inner_value in value.items():
                if isinstance(inner_value, QCheckBox):
                    detail_part[key][inner_key] = inner_value.isChecked()
                else:
                    detail_part[key][inner_key] = inner_value.currentText()
        return [first_part, detail_part]


# 程序入口
if __name__ == "__main__":
    # 初始化QApplication,界面展示要包含在QApplication初始化之后,结束之前
    app = QApplication(sys.argv)
    # 初始化并展示我们的界面组件
    window = MyWidget()
    window.show()

    # 结束QApplication
    sys.exit(app.exec())
