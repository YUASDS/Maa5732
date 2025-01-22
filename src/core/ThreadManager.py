import queue
import threading
from loguru import logger
from typing import Callable
from src.core.actions import *
from src.core.TaskerManager import TASKER_MANAGER
from src.utils.parse import json2pipline
from src.utils.click import STOP


class TaskerThread(threading.Thread):
    task: dict
    task_queue = queue.Queue()
    change_func: Callable

    def __init__(self, change_func: Callable, name=None):
        threading.Thread.__init__(self, name=name)
        self.change_func = change_func

    def run(self) -> None:
        try:
            # 主要是防止启动卡顿
            TASKER_MANAGER.init()
            while True:
                task = self.task_queue.get()
                TASKER_MANAGER.tasker.post_task("1", task).wait().get()
                global STOP
                STOP.put(1)
                self.change_func()
        except Exception as e:
            logger.exception(e)

    def add_task(self, json_data: list[dict]):
        self.task_queue.put(json2pipline(json_data))
        global STOP
        STOP.queue.clear()

    def cancle_task(self):
        logger.warning("START TO STOP!!!")
        global STOP
        STOP.put(1)
        self.task_queue.queue.clear()
        if not TASKER_MANAGER.init_flag_queue.empty():
            logger.warning("START TO POST STOP!!!")
            TASKER_MANAGER.tasker.post_stop()
        return STOP
