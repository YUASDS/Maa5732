import queue
import threading
from loguru import logger

from src.core.actions import *
from src.core.TaskerManager import TASKER_MANAGER
from src.utils.parse import json2pipline


class TaskerThread(threading.Thread):
    task: dict
    action_queue = queue.Queue()

    def __init__(self, name=None):
        threading.Thread.__init__(self, name=name)

    def run(self) -> None:
        try:
            TASKER_MANAGER.init()
            logger.info("LINK START!")
            TASKER_MANAGER.tasker.post_task("1", self.task).wait().get()
        except Exception as e:
            logger.exception(e)

    def set_task(self, json_data: list[dict]):
        self.task = json2pipline(json_data)

    def cancle_task(self):
        self.task = {}
        return TASKER_MANAGER.tasker.post_stop()


tasker_thread = TaskerThread()
