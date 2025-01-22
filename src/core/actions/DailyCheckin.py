from loguru import logger
from maa.context import Context

from src.utils.configs import cfg
from src.utils.click import Click
from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction


@TASKER_MANAGER.add_action
class DailyCheckin(MyCustomAction):
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
        test_detail = clicker.ocr_rate_click("情绪检测", 0.625, 0.55)
        if test_detail and test_detail.status.succeeded:
            clicker.click_blink()
            clicker.return_home()
        logger.info(f"{self.name} Finish")
        return True

    def stop(self) -> None:
        pass
