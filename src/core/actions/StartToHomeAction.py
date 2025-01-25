import time
from loguru import logger

from maa.context import Context

from src.utils.configs import cfg
from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction
from src.utils.click import Click

name = __file__.split("\\")[-1].split(".")[0]


@TASKER_MANAGER.add_action(name)
class StartToHomeAction(MyCustomAction):

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
        logger.info(f"{name} Start")
        clicker = Click(context)
        clicker.ocr_rate_click("系统公告", 0.1, 0.1, 20, 20)
        clicker.ocr_click("进入管理局")
        # 等待进入
        time.sleep(20)
        # 处理广告
        while True:
            detail = clicker.ocr_click("今日不再弹出")
            status = detail.status.succeeded  # type: ignore
            logger.debug(f"Click:今日不再弹出 {status}")
            if not status:
                break
            clicker.click_blink()
        # 领取月卡
        detail = clicker.ocr_click("贵宾")
        if detail and detail.status.succeeded:
            clicker.click_blink()
        # 情绪检测
        test_detail = clicker.ocr_rate_click("累计奖励", 0.625, 0.55)
        if test_detail and test_detail.status.succeeded:
            clicker.back()

        logger.info(f"{name} Finish")
        return True

    def stop(self) -> None:
        pass
