import sys

from loguru import logger
from PySide6.QtWidgets import QApplication

from src.ui.ui_controller import MyWidget

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWidget()
    window.show()

    try:
        app.exec()
    except Exception as e:
        logger.exception(e)
