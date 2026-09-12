# -*- coding: utf-8 -*-
"""运行日志栏里的实时截图控件

MAA 的截图是 numpy 数组(BGR), 这里转成 QImage 后按原比例缩放显示:
窗口变大变小都不会拉伸变形, 也不依赖截图的原始内存。
"""
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy

# 截图区高度范围(像素): 太矮看不清, 太高会把日志挤没
SNAPSHOT_MIN_HEIGHT = 120
SNAPSHOT_MAX_HEIGHT = 260
PLACEHOLDER = "运行中显示实时截图"


def to_qimage(frame) -> QImage:
    """MAA 截图(numpy, BGR/BGRA/灰度) -> QImage; 无法识别时返回 None"""
    if frame is None or getattr(frame, "size", 0) == 0:
        return None
    array = np.ascontiguousarray(frame)
    if array.ndim != 3 or array.shape[0] == 0 or array.shape[1] == 0:
        return None
    height, width, channels = array.shape
    if channels >= 3:
        # MaaFramework 走 OpenCV, 通道顺序是 BGR; 4 通道时丢掉 alpha
        if channels > 3:
            array = np.ascontiguousarray(array[:, :, :3])
        image = QImage(
            array.data, width, height, width * 3, QImage.Format.Format_BGR888
        )
    else:
        image = QImage(
            array.data, width, height, width, QImage.Format.Format_Grayscale8
        )
    # copy() 之后 QImage 自己持有像素, 原数组可以被回收
    return image.copy()


class SnapshotLabel(QLabel):
    """按原比例居中显示最新一帧截图, 没有截图时显示提示文字"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SnapshotLabel")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(SNAPSHOT_MIN_HEIGHT)
        self.setMaximumHeight(SNAPSHOT_MAX_HEIGHT)
        # 宽度交给布局, 高度按比例自己算 -> 横向可任意缩放
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        self.setText(PLACEHOLDER)
        self._frame = None

    def set_frame(self, frame) -> bool:
        """显示一帧; 转换失败时保持原画面不动"""
        image = to_qimage(frame)
        if image is None:
            return False
        self._frame = QPixmap.fromImage(image)
        self._rescale()
        return True

    def clear_frame(self) -> None:
        self._frame = None
        self.setPixmap(QPixmap())
        self.setText(PLACEHOLDER)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._rescale()

    def _rescale(self):
        if self._frame is None:
            return
        self.setPixmap(
            self._frame.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
