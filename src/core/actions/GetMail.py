from loguru import logger
from maa.context import Context

from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction
from src.utils.configs import cfg
from src.utils.click import Click


@TASKER_MANAGER.add_action
class GetMail(MyCustomAction):
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
        logger.info(f"{self.name} Start")
        clicker = Click(context)
        clicker.ocr_click("邮箱")
        clicker.ocr_click("快速处理")
        clicker.return_home()
        logger.info(f"{self.name} Finish")
        return True

    def stop(self) -> None:

        pass
