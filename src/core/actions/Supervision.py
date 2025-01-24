import time

from loguru import logger
from maa.context import Context
from maa.custom_action import CustomAction

from src.utils.configs import cfg
from src.utils.click import Click
from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction

name = __file__.split("\\")[-1].split(".")[0]


@TASKER_MANAGER.add_action(name)
class Supervision(MyCustomAction):

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
        logger.info(f"{name} Start")
        clicker = Click(context)
        #  点击危机管理-OCR识别率低
        clicker.click_rate(0.74, 0.89)
        clicker.ocr_click("监察密令")
        clicker.ocr_click("任务")
        clicker.ocr_click("每日")
        clicker.ocr_click("一键领取")
        clicker.click_rate(0.2, 0.3)
        clicker.ocr_click("领取")
        clicker.ocr_click("每周")
        clicker.ocr_click("一键领取")
        clicker.click_rate(0.2, 0.3)
        clicker.ocr_click("密令", roi=[0, 0, 0.5, 0.6])
        clicker.ocr_click("一键领取")
        clicker.click_rate(0.2, 0.3)
        clicker.ocr_click("监察", roi=[0.5, 0.5, 1, 1])
        clicker.ocr_click("一键领取", roi=[0.5, 0.5, 1, 1])
        clicker.click_rate(0.2, 0.3)
        clicker.return_home()
        logger.info(f"{name} Finish")
        return True

    def stop(self) -> None:

        pass
