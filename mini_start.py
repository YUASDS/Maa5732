# python -m pip install maafw
import os
from maa.resource import Resource
from maa.controller import AdbController
from maa.tasker import Tasker
from maa.toolkit import Toolkit

from maa.custom_recognition import CustomRecognition
from maa.custom_action import CustomAction
from maa.notification_handler import NotificationHandler, NotificationType
from maa.define import MaaAdbInputMethodEnum
from src.utils.parse import *
from src.utils.adb import change_size
from src.utils.configs import cfg
from loguru import logger


def main():

    current_dir = os.getcwd()
    adb_dir = os.path.join(current_dir, "assets", "adb", "adb.exe")
    Toolkit.init_option(os.path.join(current_dir, "assets"))
    # Toolkit.init_option(user_path)

    resource = Resource()
    res_job = resource.post_bundle("assets/resource")
    res_job.wait()

    adb_devices = Toolkit.find_adb_devices(adb_dir)
    if not adb_devices:
        print("No ADB device found.")
        exit()

    # print(adb_devices)
    # for demo, we just use the first device
    device = adb_devices[0]
    change_size(device.address)

    controller = AdbController(
        adb_path=device.adb_path,
        address=device.address,
        # screencap_methods=device.screencap_methods,
        input_methods=MaaAdbInputMethodEnum.MinitouchAndAdbKey,
        # config=device.config,
    )

    controller.post_connection().wait()
    tasker = Tasker()
    # tasker = Tasker(notification_handler=MyNotificationHandler())
    tasker.bind(resource, controller)

    if not tasker.inited:
        print("Failed to init MAA.")
        exit()

    resource.register_custom_recognition("MyRec", MyRecongition())

    task_detail = swape(tasker, [0.965, 0.5, 10, 10], [0.1, 0.6, 10, 10], 500)
    print(task_detail.status.succeeded)
    # do something with task_detail


def swape(tasker: Tasker, start, end, duration):
    import random

    if start[0] < 1:
        start[0] = start[0] * cfg.width
        start[1] = start[1] * cfg.height
        end[0] = end[0] * cfg.width
        end[1] = end[1] * cfg.height
    random_num = random.random()
    logger.debug(f"StartSwape_{random_num}:{start} {end}")

    detail = tasker.post_task(
        f"Swipe_{random_num}",
        {
            f"Swipe_{random_num}": {
                "action": "Swipe",
                "begin": start,
                "end": end,
                "duration": duration,
            }
        },
    )
    logger.debug(f"StartSwape_{random_num} Finish")
    return detail


class MyRecongition(CustomRecognition):

    def analyze(
        self,
        context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        reco_detail = context.run_recognition(
            "MyCustomOCR",
            argv.image,
            pipeline_override={"MyCustomOCR": {"roi": [100, 100, 200, 300]}},
        )

        # context is a reference, will override the pipeline for whole task
        context.override_pipeline({"MyCustomOCR": {"roi": [1, 1, 114, 514]}})
        # context.run_recognition ...

        # make a new context to override the pipeline, only for itself
        new_context = context.clone()
        new_context.override_pipeline({"MyCustomOCR": {"roi": [100, 200, 300, 400]}})
        reco_detail = new_context.run_recognition("MyCustomOCR", argv.image)

        click_job = context.tasker.controller.post_click(10, 20)
        click_job.wait()

        # context.override_next(argv., ["TaskA", "TaskB"])

        return CustomRecognition.AnalyzeResult(
            box=(0, 0, 100, 100), detail="Hello World!"
        )


class MyNotificationHandler(NotificationHandler):
    def on_resource_loading(
        self,
        noti_type: NotificationType,
        detail: NotificationHandler.ResourceLoadingDetail,
    ):
        print(f"on_resource_loading: {noti_type}, {detail}")

    def on_controller_action(
        self,
        noti_type: NotificationType,
        detail: NotificationHandler.ControllerActionDetail,
    ):
        print(f"on_controller_action: {noti_type}, {detail}")

    def on_tasker_task(
        self, noti_type: NotificationType, detail: NotificationHandler.TaskerTaskDetail
    ):
        print(f"on_tasker_task: {noti_type}, {detail}")

    def on_node_next_list(
        self,
        noti_type: NotificationType,
        detail: NotificationHandler.NodeActionDetail,
    ):
        print(f"on_node_next_list: {noti_type}, {detail}")

    def on_node_recognition(
        self,
        noti_type: NotificationType,
        detail: NotificationHandler.NodeActionDetail,
    ):
        print(f"on_node_recognition: {noti_type}, {detail}")

    def on_node_action(
        self,
        noti_type: NotificationType,
        detail: NotificationHandler.NodeActionDetail,
    ):
        print(f"on_node_action: {noti_type}, {detail}")


if __name__ == "__main__":
    main()
