# -*- coding: UTF-8 -*-
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QPushButton,
    QWidget,
    QVBoxLayout,
    QFrame,
    QStyle,
    QLabel,
    QScrollArea,
)


class NavButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setObjectName("NavButton")
        self._full_text = text
        self.setCheckable(True)
        self.setFixedHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(text)

    def setText(self, text):
        self._full_text = text if text else self._full_text
        super().setText("")  # 默认不显示文本

    def showFullText(self, show=True):
        super().setText(self._full_text if show else "")


class NavigationBar(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.setObjectName("NavigationBar")
        self.expanded = False
        self.setFixedWidth(64)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 顶部标题区域
        title_frame = QFrame()
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)

        self.menu_btn = NavButton("菜单")
        self.menu_btn.setIcon(QIcon("assets/icons/svg_icons/menu-burger.svg"))
        self.menu_btn.setIconSize(QSize(22, 22))
        self.menu_btn.clicked.connect(self.toggle_navigation)
        title_layout.addWidget(self.menu_btn)

        main_layout.addWidget(title_frame)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 禁用水平滚动条

        nav_container = QWidget()
        self.nav_layout = QVBoxLayout(nav_container)
        self.nav_layout.setSpacing(2)
        self.nav_layout.setContentsMargins(0, 10, 0, 10)

        self.add_nav_button("首页", "assets/icons/svg_icons/home.svg")
        for program in self.controller.programs.programs:
            print(program.program_name, program.program_icon)
            self.add_nav_button(program.program_name, f"assets{program.program_icon}")
        self.nav_layout.addStretch()
        self.add_nav_button("刷新资源", "assets/icons/svg_icons/refresh.svg")
        self.add_nav_button("设置", "assets/icons/svg_icons/settings-sliders.svg")

        scroll.setWidget(nav_container)
        main_layout.addWidget(scroll)

        # 存储按钮引用
        self.buttons = [
            widget
            for i in range(self.nav_layout.count())
            if isinstance(widget := self.nav_layout.itemAt(i).widget(), NavButton)
        ]

    def add_nav_button(self, text, icon_path=None):
        button = NavButton(text)
        # 如果指定了图标路径，则使用该路径的图标；否则使用默认的样式图标
        if icon_path:
            icon = QIcon(icon_path)
        else:
            icon = self.style().standardIcon(QStyle.SP_BrowserReload)
        button.setIcon(icon)
        button.setIconSize(QSize(22, 22))
        button.clicked.connect(lambda: button.setChecked(False))
        self.nav_layout.addWidget(button)
        return button

    def toggle_navigation(self):
        target_width = 200 if not self.expanded else 64
        self.width_anim = QPropertyAnimation(self, b"minimumWidth")
        self.width_anim.setDuration(300)
        self.width_anim.setStartValue(self.width())
        self.width_anim.setEndValue(target_width)
        self.width_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.expanded = not self.expanded

        if self.expanded:
            for button in self.buttons:
                button.showFullText(True)
        else:
            for button in self.buttons:
                button.showFullText(False)

        self.width_anim.start()
