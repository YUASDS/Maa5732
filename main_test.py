from src.core import actions
from src.core.TaskerManager import TASKER_MANAGER

if __name__ == "__main__":
    task = TASKER_MANAGER
    task.init()
    task.tasker.post_task(
        "6",
        {
            "1": {
                "action": "custom",
                # "target": [0, 0, 100, 100],
                "custom_action": "StartToHomeAction",
                "next": "2",
            },
            "2": {
                "action": "custom",
                # "target": [0, 0, 100, 100],
                "custom_action": "DailyCheckin",
                "next": "3",
            },
            "3": {
                "action": "custom",
                # "target": [0, 0, 100, 100],
                "custom_action": "Guild",
                "next": "4",
            },
            "4": {
                "action": "custom",
                # "target": [0, 0, 100, 100],
                "custom_action": "GetMail",
                "next": "5",
            },
            "5": {
                "action": "custom",
                # "target": [0, 0, 100, 100],
                "custom_action": "Purchase",
                "next": "6",
            },
            "6": {
                "action": "custom",
                # "target": [0, 0, 100, 100],
                "custom_action": "Guild",
            },
        },
    ).wait().get()
