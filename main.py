import sys
import datetime
from loguru import logger
from PySide6.QtWidgets import QApplication

from src.ui.ui_controller import MyWidget

now_time = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
logger.add(f"assets/logs/{now_time}.log")
version = "0.1.3"
if __name__ == "__main__":
    logger.info(f"Start MAA_5732 {version}")
    app = QApplication(sys.argv)
    window = MyWidget()
    window.show()

    try:
        app.exec()
    except Exception as e:
        logger.exception(e)
