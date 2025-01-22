import queue
from loguru import logger

from maa.resource import Resource
from maa.controller import AdbController
from maa.tasker import Tasker
from maa.toolkit import Toolkit
from maa.custom_action import CustomAction
from maa.define import MaaAdbInputMethodEnum
from maa.context import Context

from src.utils.configs import cfg
from src.utils.adb import change_size


class MyCustomAction(CustomAction):
    name: str

    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        return False

    def stop(self) -> None:
        pass


class TaskerManager:
    resource: Resource
    controller: AdbController
    tasker: Tasker
    custon_action: dict = {}
    init_flag_queue: queue.Queue = queue.Queue()

    def __init__(self) -> None:
        pass

    def init(self) -> None:
        Toolkit.init_option(cfg.tool_kit_option)
        # Toolkit.init_option(user_path)

        self.resource = Resource()
        res_job = self.resource.post_bundle("assets/resource")
        res_job.wait()

        adb_devices = Toolkit.find_adb_devices(cfg.adb_dir)
        if not adb_devices:
            print("No ADB device found.")
            exit()

        # for demo, we just use the first device
        device = adb_devices[0]
        # 自适应分辨率
        change_size(device.address)
        self.controller = AdbController(
            adb_path=device.adb_path,
            address=device.address,
            screencap_methods=device.screencap_methods,
            input_methods=MaaAdbInputMethodEnum.AdbShell,
            config={},
            # config=device.config,
        )
        self.controller.post_connection().wait()
        self.tasker = Tasker()
        # tasker = Tasker(notification_handler=MyNotificationHandler())
        self.tasker.bind(self.resource, self.controller)
        self._register_custom_action()
        self.init_flag_queue.put(1)
        logger.info("Init successeed!!!")

    def add_action(self, custon_action: type[MyCustomAction]):
        self.custon_action[custon_action.name] = custon_action
        logger.debug(f"load {custon_action.name}")
        return custon_action

    def _register_custom_action(self):
        for key, value in self.custon_action.items():
            self.resource.register_custom_action(key, value())  # type: ignore


TASKER_MANAGER = TaskerManager()
