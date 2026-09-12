import os
import sys
import time
import shutil
import datetime
from loguru import logger
from PySide6.QtWidgets import QApplication

from src.ui.ui_controller import MyWidget
from src.ui.theme import apply_theme
from src.utils.console import attach_parent_console
from src.utils.paths import BASE_DIR

LOG_KEEP_DAYS = 7
LOG_DIR = os.path.join(BASE_DIR, "logs")
# 控制台日志级别,可用环境变量 MAA5732_LOG_LEVEL 调整(如 DEBUG)
LOG_LEVEL = os.environ.get("MAA5732_LOG_LEVEL", "INFO").upper()
LOG_FORMAT = (
    "<green>{time:HH:mm:ss}</green> | <level>{level: <7}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)


def clean_old_logs(days=LOG_KEEP_DAYS):
    """清理logs目录中超过指定天数的日志文件"""
    cutoff = time.time() - days * 86400
    if not os.path.isdir(LOG_DIR):
        return
    for name in os.listdir(LOG_DIR):
        path = os.path.join(LOG_DIR, name)
        try:
            if os.path.isfile(path) and os.path.getmtime(path) < cutoff:
                os.remove(path)
        except OSError:
            continue


def clean_update_dir():
    """清理上次更新遗留的临时目录(仅打包环境)"""
    if getattr(sys, "frozen", False):
        update_dir = os.path.join(os.path.dirname(sys.executable), "update")
        if os.path.isdir(update_dir):
            shutil.rmtree(update_dir, ignore_errors=True)


def setup_logging() -> bool:
    """配置日志: 控制台(可用时) + 文件双通道,返回控制台是否可用"""
    console_ready = attach_parent_console()
    # 去掉默认 stderr sink,避免重复输出或写入已失效的流
    logger.remove()
    if console_ready:
        try:
            colorize = bool(sys.stderr.isatty())
        except Exception:
            colorize = False
        logger.add(sys.stderr, level=LOG_LEVEL, format=LOG_FORMAT, colorize=colorize)
    logger.add(os.path.join(LOG_DIR, f"{now_time}.log"), level="DEBUG")
    if console_ready:
        logger.info(f"日志目录: {LOG_DIR} | 终端级别: {LOG_LEVEL}")
    return console_ready


now_time = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
os.makedirs(LOG_DIR, exist_ok=True)
clean_old_logs()
clean_update_dir()
setup_logging()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_theme(app)
    window = MyWidget()
    window.show()

    try:
        app.exec()
    except Exception as e:
        logger.exception(e)
