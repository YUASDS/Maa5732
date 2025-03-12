import sys
import datetime
from loguru import logger
from PySide6.QtWidgets import QApplication

from src.ui.ui_controller import MyWidget

now_time = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
logger.add(f"assets/logs/{now_time}.log")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWidget()
    window.show()

    try:
        app.exec()
    except Exception as e:
        logger.exception(e)
