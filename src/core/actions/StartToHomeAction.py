import time
from loguru import logger

from maa.context import Context

from src.utils.configs import cfg
from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction


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
        context.run_task(
            "click_blink",
            {"click_blink": {"action": "Click", "target": [0, 0, 100, 100]}},
        )
        time.sleep(cfg.sleep_time)
        # 点击预设
        logger.debug("StartClick:进入管理局")
        context.run_task(
            "进入管理局",
            {
                "进入管理局": {
                    "timeout": 1000,
                    "recognition": "OCR",
                    "expected": "进入管理局",
                    "action": "Click",
                },
            },
        )
        time.sleep(3)
        # context.run_action("Click", [0, 0, 100, 100])
        status = True
        while status:
            detail = context.run_task(
                "公告",
                {
                    "公告": {
                        "timeout": 1000,
                        "recognition": "OCR",
                        "expected": "今日不再弹出",
                        "action": "Click",
                    },
                },
            )
            time.sleep(cfg.sleep_time)
            context.run_task(
                "click_blink",
                {"click_blink": {"action": "Click", "target": [0, 0, 100, 100]}},
            )
            status = detail.status.succeeded  # type: ignore
            logger.debug(f"Click:今日不再弹出 {status}")
        logger.info(f"{self.name} Finish")
        return True

    def stop(self) -> None:
        pass
