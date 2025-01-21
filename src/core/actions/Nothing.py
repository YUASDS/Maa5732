import time

from loguru import logger
from maa.context import Context


from src.utils.configs import cfg
from src.utils.click import Click
from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction


@TASKER_MANAGER.add_action
class Nothing(MyCustomAction):
    name = __file__.split("\\")[-1].split(".")[0]

    def run(
        self,
        context: Context,
        argv: MyCustomAction.RunArg,
    ) -> bool:
        """
        :param argv:
        :param context: 运行上下文
        :return: 是否执行成功。
        """
        return True

    def stop(self) -> None:

        pass
