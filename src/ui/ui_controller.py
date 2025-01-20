# 导入sys
import sys

# 任何一个PySide界面程序都需要使用QApplication
# 我们要展示一个普通的窗口，所以需要导入QWidget，用来让我们自己的类继承
from PySide6.QtWidgets import QApplication, QWidget, QPushButton

# 导入我们生成的界面
from ui import Ui_Form


# 继承QWidget类，以获取其属性和方法
class MyWidget(QWidget):
    order = {}
    state = 0

    def __init__(self):
        super().__init__()
        # 设置界面为我们生成的界面
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.GuildButton.clicked.connect(self.buttonClick)
        self.ui.RaidButton.clicked.connect(self.buttonClick)
        self.ui.StartButton.clicked.connect(self.buttonClick)
        self.ui.FriendsButton.clicked.connect(self.buttonClick)
        self.ui.PurchaseButton.clicked.connect(self.buttonClick)
        self.ui.SupervisionButton.clicked.connect(self.buttonClick)
        self.ui.LinkStartButton.clicked.connect(self.start)

        self.ui.SlectAllButton.clicked.connect(self.select_all)
        self.ui.ClearAllButton.clicked.connect(self.clear_all)

        self.ui.GuildcheckBox.clicked.connect(self.checkBox)
        self.ui.RaidcheckBox.clicked.connect(self.checkBox)
        self.ui.StartcheckBox.clicked.connect(self.checkBox)
        self.ui.FriendscheckBox.clicked.connect(self.checkBox)
        self.ui.PurchasecheckBox.clicked.connect(self.checkBox)
        self.ui.SupervisioncheckBox.clicked.connect(self.checkBox)
        self.ui.ConstructioncheckBox.clicked.connect(self.checkBox)
        self.ui.DailyCheckincheckBox.clicked.connect(self.checkBox)
        self.ui.BureaucheckBox.clicked.connect(self.checkBox)

        self.init_combo()

    def init_combo(self):
        self.ui.GuildCombo.addItems(["狄斯币", "异方晶"])
        self.ui.ResourceCombo.addItems(["狄斯币", "狂厄结晶"])
        self.ui.SupervisionRewardCombo.addItems(["a", "b"])

    def checkBox(self):
        box = self.sender()
        boxName = box.objectName()
        print(boxName)

    def select_all(self):
        self.ui.GuildcheckBox.setChecked(True)
        self.ui.RaidcheckBox.setChecked(True)
        self.ui.StartcheckBox.setChecked(True)
        self.ui.FriendscheckBox.setChecked(True)
        self.ui.PurchasecheckBox.setChecked(True)
        self.ui.SupervisioncheckBox.setChecked(True)
        self.ui.BureaucheckBox.setChecked(True)
        self.ui.ConstructioncheckBox.setChecked(True)
        self.ui.DailyCheckincheckBox.setChecked(True)

    def clear_all(self):
        self.ui.GuildcheckBox.setChecked(False)
        self.ui.BureaucheckBox.setChecked(False)
        self.ui.RaidcheckBox.setChecked(False)
        self.ui.StartcheckBox.setChecked(False)
        self.ui.FriendscheckBox.setChecked(False)
        self.ui.PurchasecheckBox.setChecked(False)
        self.ui.SupervisioncheckBox.setChecked(False)
        self.ui.ConstructioncheckBox.setChecked(False)
        self.ui.DailyCheckincheckBox.setChecked(False)

    def buttonClick(self):
        btn = self.sender()
        btnName = btn.objectName()
        if btnName == "RaidButton":
            self.ui.stackedWidget.setCurrentWidget(self.ui.Raid)
        if btnName == "GuildButton":
            self.ui.stackedWidget.setCurrentWidget(self.ui.Guild)
        if btnName == "StartButton":
            self.ui.stackedWidget.setCurrentWidget(self.ui.Start)
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

    def start(self):

        if self.state == 0:
            self.ui.LinkStartButton.setText("Stop")
            self.state = 1
        else:
            self.ui.LinkStartButton.setText("Link Start!")
            self.state = 0


# 程序入口
if __name__ == "__main__":
    # 初始化QApplication，界面展示要包含在QApplication初始化之后，结束之前
    app = QApplication(sys.argv)

    # 初始化并展示我们的界面组件
    window = MyWidget()
    window.show()

    # 结束QApplication
    sys.exit(app.exec())
