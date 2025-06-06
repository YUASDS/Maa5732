# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'maa-5732.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGroupBox,
    QHBoxLayout, QPushButton, QSizePolicy, QStackedWidget,
    QTabWidget, QTextBrowser, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(642, 543)
        self.verticalLayout_3 = QVBoxLayout(Form)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.tabWidget = QTabWidget(Form)
        self.tabWidget.setObjectName(u"tabWidget")
        self.working = QWidget()
        self.working.setObjectName(u"working")
        self.verticalLayout_2 = QVBoxLayout(self.working)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.SelectBox = QGroupBox(self.working)
        self.SelectBox.setObjectName(u"SelectBox")
        self.verticalLayout = QVBoxLayout(self.SelectBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.StartToHomeActioncheckBox = QCheckBox(self.SelectBox)
        self.StartToHomeActioncheckBox.setObjectName(u"StartToHomeActioncheckBox")
        self.StartToHomeActioncheckBox.setChecked(True)

        self.horizontalLayout.addWidget(self.StartToHomeActioncheckBox)

        self.StartButton = QPushButton(self.SelectBox)
        self.StartButton.setObjectName(u"StartButton")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentProperties))
        self.StartButton.setIcon(icon)
        self.StartButton.setCheckable(False)
        self.StartButton.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.StartButton)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.GuildcheckBox = QCheckBox(self.SelectBox)
        self.GuildcheckBox.setObjectName(u"GuildcheckBox")
        self.GuildcheckBox.setChecked(True)

        self.horizontalLayout_3.addWidget(self.GuildcheckBox)

        self.GuildButton = QPushButton(self.SelectBox)
        self.GuildButton.setObjectName(u"GuildButton")
        self.GuildButton.setIcon(icon)

        self.horizontalLayout_3.addWidget(self.GuildButton)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.GetMailcheckBox = QCheckBox(self.SelectBox)
        self.GetMailcheckBox.setObjectName(u"GetMailcheckBox")
        self.GetMailcheckBox.setChecked(True)

        self.horizontalLayout_17.addWidget(self.GetMailcheckBox)


        self.verticalLayout.addLayout(self.horizontalLayout_17)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.PurchasecheckBox = QCheckBox(self.SelectBox)
        self.PurchasecheckBox.setObjectName(u"PurchasecheckBox")
        self.PurchasecheckBox.setChecked(True)

        self.horizontalLayout_4.addWidget(self.PurchasecheckBox)

        self.PurchaseButton = QPushButton(self.SelectBox)
        self.PurchaseButton.setObjectName(u"PurchaseButton")
        self.PurchaseButton.setIcon(icon)

        self.horizontalLayout_4.addWidget(self.PurchaseButton)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.ConstructioncheckBox = QCheckBox(self.SelectBox)
        self.ConstructioncheckBox.setObjectName(u"ConstructioncheckBox")
        self.ConstructioncheckBox.setChecked(True)

        self.horizontalLayout_5.addWidget(self.ConstructioncheckBox)


        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.BureaucheckBox = QCheckBox(self.SelectBox)
        self.BureaucheckBox.setObjectName(u"BureaucheckBox")
        self.BureaucheckBox.setChecked(True)

        self.horizontalLayout_6.addWidget(self.BureaucheckBox)


        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.FriendscheckBox = QCheckBox(self.SelectBox)
        self.FriendscheckBox.setObjectName(u"FriendscheckBox")
        self.FriendscheckBox.setChecked(True)

        self.horizontalLayout_7.addWidget(self.FriendscheckBox)

        self.FriendsButton = QPushButton(self.SelectBox)
        self.FriendsButton.setObjectName(u"FriendsButton")
        self.FriendsButton.setIcon(icon)

        self.horizontalLayout_7.addWidget(self.FriendsButton)


        self.verticalLayout.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.RaidcheckBox = QCheckBox(self.SelectBox)
        self.RaidcheckBox.setObjectName(u"RaidcheckBox")
        self.RaidcheckBox.setChecked(True)

        self.horizontalLayout_9.addWidget(self.RaidcheckBox)

        self.RaidButton = QPushButton(self.SelectBox)
        self.RaidButton.setObjectName(u"RaidButton")
        self.RaidButton.setIcon(icon)

        self.horizontalLayout_9.addWidget(self.RaidButton)


        self.verticalLayout.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.SupervisioncheckBox = QCheckBox(self.SelectBox)
        self.SupervisioncheckBox.setObjectName(u"SupervisioncheckBox")
        self.SupervisioncheckBox.setChecked(True)

        self.horizontalLayout_10.addWidget(self.SupervisioncheckBox)

        self.SupervisionButton = QPushButton(self.SelectBox)
        self.SupervisionButton.setObjectName(u"SupervisionButton")
        self.SupervisionButton.setIcon(icon)

        self.horizontalLayout_10.addWidget(self.SupervisionButton)


        self.verticalLayout.addLayout(self.horizontalLayout_10)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.SlectAllButton = QPushButton(self.SelectBox)
        self.SlectAllButton.setObjectName(u"SlectAllButton")

        self.horizontalLayout_12.addWidget(self.SlectAllButton)

        self.ClearAllButton = QPushButton(self.SelectBox)
        self.ClearAllButton.setObjectName(u"ClearAllButton")

        self.horizontalLayout_12.addWidget(self.ClearAllButton)


        self.verticalLayout.addLayout(self.horizontalLayout_12)


        self.horizontalLayout_8.addWidget(self.SelectBox)

        self.SettingBox = QGroupBox(self.working)
        self.SettingBox.setObjectName(u"SettingBox")
        self.horizontalLayout_14 = QHBoxLayout(self.SettingBox)
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.stackedWidget = QStackedWidget(self.SettingBox)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.StartToHomeAction = QWidget()
        self.StartToHomeAction.setObjectName(u"StartToHomeAction")
        self.StartToHomeAction.setEnabled(True)
        self.StartToHomeAction.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.StartToHomeAction.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.verticalLayout_12 = QVBoxLayout(self.StartToHomeAction)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.StartToHomeAction_StartAPPcheckBox = QCheckBox(self.StartToHomeAction)
        self.StartToHomeAction_StartAPPcheckBox.setObjectName(u"StartToHomeAction_StartAPPcheckBox")
        self.StartToHomeAction_StartAPPcheckBox.setCheckable(True)
        self.StartToHomeAction_StartAPPcheckBox.setChecked(False)

        self.verticalLayout_12.addWidget(self.StartToHomeAction_StartAPPcheckBox)

        self.StartToHomeAction_ServerCheckcomboBox = QComboBox(self.StartToHomeAction)
        self.StartToHomeAction_ServerCheckcomboBox.setObjectName(u"StartToHomeAction_ServerCheckcomboBox")
        self.StartToHomeAction_ServerCheckcomboBox.setEnabled(True)
        self.StartToHomeAction_ServerCheckcomboBox.setEditable(False)

        self.verticalLayout_12.addWidget(self.StartToHomeAction_ServerCheckcomboBox)

        self.stackedWidget.addWidget(self.StartToHomeAction)
        self.Guild = QWidget()
        self.Guild.setObjectName(u"Guild")
        self.verticalLayout_11 = QVBoxLayout(self.Guild)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.Guild_GuildCombo = QComboBox(self.Guild)
        self.Guild_GuildCombo.setObjectName(u"Guild_GuildCombo")

        self.verticalLayout_11.addWidget(self.Guild_GuildCombo)

        self.stackedWidget.addWidget(self.Guild)
        self.Purchase = QWidget()
        self.Purchase.setObjectName(u"Purchase")
        self.verticalLayout_10 = QVBoxLayout(self.Purchase)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.Purchase_FriendShopcheckBox = QCheckBox(self.Purchase)
        self.Purchase_FriendShopcheckBox.setObjectName(u"Purchase_FriendShopcheckBox")
        self.Purchase_FriendShopcheckBox.setChecked(True)

        self.verticalLayout_6.addWidget(self.Purchase_FriendShopcheckBox)

        self.Purchase_ActivityShopcheckBox = QCheckBox(self.Purchase)
        self.Purchase_ActivityShopcheckBox.setObjectName(u"Purchase_ActivityShopcheckBox")
        self.Purchase_ActivityShopcheckBox.setChecked(True)

        self.verticalLayout_6.addWidget(self.Purchase_ActivityShopcheckBox)

        self.Purchase_FreeShopcheckBox = QCheckBox(self.Purchase)
        self.Purchase_FreeShopcheckBox.setObjectName(u"Purchase_FreeShopcheckBox")
        self.Purchase_FreeShopcheckBox.setChecked(True)

        self.verticalLayout_6.addWidget(self.Purchase_FreeShopcheckBox)


        self.verticalLayout_10.addLayout(self.verticalLayout_6)

        self.stackedWidget.addWidget(self.Purchase)
        self.Friends = QWidget()
        self.Friends.setObjectName(u"Friends")
        self.verticalLayout_5 = QVBoxLayout(self.Friends)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.Friends_FriendPointcheckBox = QCheckBox(self.Friends)
        self.Friends_FriendPointcheckBox.setObjectName(u"Friends_FriendPointcheckBox")
        self.Friends_FriendPointcheckBox.setChecked(True)

        self.verticalLayout_4.addWidget(self.Friends_FriendPointcheckBox)

        self.Friends_AutoLikecheckBox = QCheckBox(self.Friends)
        self.Friends_AutoLikecheckBox.setObjectName(u"Friends_AutoLikecheckBox")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Friends_AutoLikecheckBox.sizePolicy().hasHeightForWidth())
        self.Friends_AutoLikecheckBox.setSizePolicy(sizePolicy)
        self.Friends_AutoLikecheckBox.setChecked(True)

        self.verticalLayout_4.addWidget(self.Friends_AutoLikecheckBox)

        self.verticalLayout_4.setStretch(0, 1)

        self.verticalLayout_5.addLayout(self.verticalLayout_4)

        self.stackedWidget.addWidget(self.Friends)
        self.Raid = QWidget()
        self.Raid.setObjectName(u"Raid")
        self.verticalLayout_9 = QVBoxLayout(self.Raid)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.Raid_RaidDarkcheckBox = QCheckBox(self.Raid)
        self.Raid_RaidDarkcheckBox.setObjectName(u"Raid_RaidDarkcheckBox")
        self.Raid_RaidDarkcheckBox.setChecked(True)

        self.verticalLayout_7.addWidget(self.Raid_RaidDarkcheckBox)

        self.Raid_RaidRivercheckBox = QCheckBox(self.Raid)
        self.Raid_RaidRivercheckBox.setObjectName(u"Raid_RaidRivercheckBox")
        self.Raid_RaidRivercheckBox.setChecked(True)

        self.verticalLayout_7.addWidget(self.Raid_RaidRivercheckBox)

        self.Raid_StromLevelCombo = QComboBox(self.Raid)
        self.Raid_StromLevelCombo.setObjectName(u"Raid_StromLevelCombo")

        self.verticalLayout_7.addWidget(self.Raid_StromLevelCombo)

        self.Raid_RaidFightcheckBox = QCheckBox(self.Raid)
        self.Raid_RaidFightcheckBox.setObjectName(u"Raid_RaidFightcheckBox")

        self.verticalLayout_7.addWidget(self.Raid_RaidFightcheckBox)

        self.Raid_ResourceCombo = QComboBox(self.Raid)
        self.Raid_ResourceCombo.setObjectName(u"Raid_ResourceCombo")

        self.verticalLayout_7.addWidget(self.Raid_ResourceCombo)

        self.Raid_ResourceLevelCombo = QComboBox(self.Raid)
        self.Raid_ResourceLevelCombo.setObjectName(u"Raid_ResourceLevelCombo")

        self.verticalLayout_7.addWidget(self.Raid_ResourceLevelCombo)


        self.verticalLayout_9.addLayout(self.verticalLayout_7)

        self.stackedWidget.addWidget(self.Raid)
        self.Supervision = QWidget()
        self.Supervision.setObjectName(u"Supervision")
        self.verticalLayout_8 = QVBoxLayout(self.Supervision)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.Supervision_RewardCombo = QComboBox(self.Supervision)
        self.Supervision_RewardCombo.setObjectName(u"Supervision_RewardCombo")

        self.verticalLayout_8.addWidget(self.Supervision_RewardCombo)

        self.stackedWidget.addWidget(self.Supervision)
        self.RestPage_2 = QWidget()
        self.RestPage_2.setObjectName(u"RestPage_2")
        self.stackedWidget.addWidget(self.RestPage_2)
        self.RestPage_1 = QWidget()
        self.RestPage_1.setObjectName(u"RestPage_1")
        self.stackedWidget.addWidget(self.RestPage_1)

        self.horizontalLayout_14.addWidget(self.stackedWidget)


        self.horizontalLayout_8.addWidget(self.SettingBox)

        self.LogBox = QGroupBox(self.working)
        self.LogBox.setObjectName(u"LogBox")
        self.horizontalLayout_11 = QHBoxLayout(self.LogBox)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.textBrowser = QTextBrowser(self.LogBox)
        self.textBrowser.setObjectName(u"textBrowser")

        self.horizontalLayout_11.addWidget(self.textBrowser)


        self.horizontalLayout_8.addWidget(self.LogBox)

        self.horizontalLayout_8.setStretch(0, 1)
        self.horizontalLayout_8.setStretch(1, 1)
        self.horizontalLayout_8.setStretch(2, 1)

        self.verticalLayout_2.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.LinkStartButton = QPushButton(self.working)
        self.LinkStartButton.setObjectName(u"LinkStartButton")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.LinkStartButton.sizePolicy().hasHeightForWidth())
        self.LinkStartButton.setSizePolicy(sizePolicy1)

        self.horizontalLayout_15.addWidget(self.LinkStartButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout_15)

        self.tabWidget.addTab(self.working, "")
        self.tools = QWidget()
        self.tools.setObjectName(u"tools")
        self.tabWidget.addTab(self.tools, "")
        self.settings = QWidget()
        self.settings.setObjectName(u"settings")
        self.settings.setMouseTracking(False)
        self.tabWidget.addTab(self.settings, "")

        self.verticalLayout_3.addWidget(self.tabWidget)


        self.retranslateUi(Form)

        self.tabWidget.setCurrentIndex(0)
        self.stackedWidget.setCurrentIndex(4)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Maa5732", None))
        self.SelectBox.setTitle("")
        self.StartToHomeActioncheckBox.setText(QCoreApplication.translate("Form", u"\u542f\u52a8", None))
        self.StartButton.setText("")
        self.GuildcheckBox.setText(QCoreApplication.translate("Form", u"\u5de5\u4f1a\u6350\u8d60", None))
        self.GuildButton.setText("")
        self.GetMailcheckBox.setText(QCoreApplication.translate("Form", u"\u90ae\u4ef6\u9886\u53d6", None))
        self.PurchasecheckBox.setText(QCoreApplication.translate("Form", u"\u91c7\u8d2d\u4e2d\u5fc3", None))
        self.PurchaseButton.setText("")
        self.ConstructioncheckBox.setText(QCoreApplication.translate("Form", u"\u57fa\u5efa\u6536\u83dc", None))
        self.BureaucheckBox.setText(QCoreApplication.translate("Form", u"\u7ba1\u7406\u5c40", None))
        self.FriendscheckBox.setText(QCoreApplication.translate("Form", u"\u597d\u53cb", None))
        self.FriendsButton.setText("")
        self.RaidcheckBox.setText(QCoreApplication.translate("Form", u"\u526f\u672c", None))
        self.RaidButton.setText("")
        self.SupervisioncheckBox.setText(QCoreApplication.translate("Form", u"\u76d1\u5bdf\u5bc6\u4ee4", None))
        self.SupervisionButton.setText("")
        self.SlectAllButton.setText(QCoreApplication.translate("Form", u"\u5168\u9009", None))
        self.ClearAllButton.setText(QCoreApplication.translate("Form", u"\u6e05\u7a7a", None))
        self.SettingBox.setTitle("")
        self.StartToHomeAction_StartAPPcheckBox.setText(QCoreApplication.translate("Form", u"\u542f\u52a8\u6e38\u620f", None))
        self.Purchase_FriendShopcheckBox.setText(QCoreApplication.translate("Form", u"\u53cb\u60c5\u70b9\u5546\u5e97", None))
        self.Purchase_ActivityShopcheckBox.setText(QCoreApplication.translate("Form", u"\u6d3b\u52a8\u5546\u5e97", None))
        self.Purchase_FreeShopcheckBox.setText(QCoreApplication.translate("Form", u"\u514d\u8d39\u4f53\u529b", None))
        self.Friends_FriendPointcheckBox.setText(QCoreApplication.translate("Form", u"\u6536\u53d6\u8d60\u9001\u53cb\u60c5\u70b9", None))
        self.Friends_AutoLikecheckBox.setText(QCoreApplication.translate("Form", u"\u81ea\u52a8\u70b9\u8d5e", None))
        self.Raid_RaidDarkcheckBox.setText(QCoreApplication.translate("Form", u"\u6df1\u4e95", None))
        self.Raid_RaidRivercheckBox.setText(QCoreApplication.translate("Form", u"\u8bb0\u5fc6\u98ce\u66b4", None))
        self.Raid_RaidFightcheckBox.setText(QCoreApplication.translate("Form", u"\u4f53\u529b\u526f\u672c", None))
        self.LogBox.setTitle("")
        self.LinkStartButton.setText(QCoreApplication.translate("Form", u"Link Start\uff01", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.working), QCoreApplication.translate("Form", u"\u4e00\u952e\u957f\u8349", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tools), QCoreApplication.translate("Form", u"\u5de5\u5177", None))
#if QT_CONFIG(accessibility)
        self.settings.setAccessibleName("")
#endif // QT_CONFIG(accessibility)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.settings), QCoreApplication.translate("Form", u"\u8bbe\u7f6e", None))
    # retranslateUi

