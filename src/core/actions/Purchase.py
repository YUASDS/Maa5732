import time

from loguru import logger
from maa.context import Context
from maa.custom_action import CustomAction

from src.utils.configs import cfg
from src.utils.click import Click
from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction


@TASKER_MANAGER.add_action
class Purchase(MyCustomAction):
    name = __file__.split("\\")[-1].split(".")[0]

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        """
        :param argv:
        :param context: 运行上下文
        :return: 是否执行成功。
        """
        logger.info(f"{self.name} Start")
        click = Click(context)
        #  点击危机管理-OCR识别率低
        click.click_rate(0.74, 0.89)
        click.ocr_click("采购办")
        click.ocr_click("精选礼包")
        for _ in range(2):
            click.swape([0.965, 0.5, 10, 10], [0.1, 0.6, 10, 10], 1000)
        click.ocr_click("每日免费补给")
        click.ocr_click("购买")
        click.click_blink()
        click.return_home()
        logger.info(f"{self.name} Finish")
        return True

    def stop(self) -> None:

        pass
