import queue
import threading

from src.core.TaskerManager import TASKER_MANAGER


class TaskerThread(threading.Thread):
    task: dict
    action_queue = queue.Queue()

    def __init__(self, name=None):
        threading.Thread.__init__(self, name=name)

    def run(self) -> None:
        TASKER_MANAGER.init()
        TASKER_MANAGER.tasker.post_task("1", self._dict2pipeline()).wait().get()

    def add_task(self, task: dict):
        self.task = task

    def cancle_task(self):
        self.task = {}
        TASKER_MANAGER.tasker.post_stop()
        pass

    def _dict2pipeline(self):
        pipline = self.task
        return pipline


tasker_thread = TaskerThread()
