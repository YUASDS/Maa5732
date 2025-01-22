import time
from loguru import logger

from maa.context import Context

from src.utils.configs import cfg
from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction
from src.utils.click import Click


@TASKER_MANAGER.add_action
class StartToHomeAction(MyCustomAction):
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
        logger.debug("Begin to click [0 0 100 100]")
        clicker = Click(context)
        clicker.click_rate(0.1, 0.1, 20, 20)
        # 点击预设
        clicker.ocr_click("进入管理局")
        # 等待进入
        time.sleep(20)
        # 领取月卡
        detail = clicker.ocr_click("贵宾")
        if detail and detail.status.succeeded:
            clicker.click_blink()
            # 情绪检测
        test_detail = clicker.ocr_rate_click("情绪检测", 0.625, 0.55)
        if test_detail and test_detail.status.succeeded:
            clicker.click_blink()
        while True:
            detail = clicker.ocr_click("今日不再弹出")
            status = detail.status.succeeded  # type: ignore
            logger.debug(f"Click:今日不再弹出 {status}")
            if not status:
                break
            clicker.click_blink()

        logger.info(f"{self.name} Finish")
        return True

    def stop(self) -> None:
        pass
