import json
from loguru import logger
from maa.context import Context

from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction
from src.utils.configs import cfg
from src.utils.click import Click

default_cfg = {"RaidRiver": True, "RaidDark": True, "RaidFight": {"resource": "狄斯币"}}

action_dict = {}


def gold_fight(context: Context):
    clicker = Click(context)
    clicker.click_rate(0.9, 0.2)


@TASKER_MANAGER.add_action
class Raid(MyCustomAction):
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
        action_param = json.loads(argv.custom_action_param)
        print(action_param)
        run_param = default_cfg.copy()
        if not action_param == {}:
            run_param = action_param
        clicker = Click(context)

        if run_param["RaidRiver"]:
            logger.info(f"RaidRiver Start")
            clicker.click_rate(0.9, 0.2)
            clicker.ocr_click("锈河")
            clicker.ocr_click("记忆风暴")
            clicker.ocr_click("4")
            clicker.ocr_click("连续扫荡")
            clicker.ocr_click("开始扫荡")
            clicker.ocr_click("完成", 10)
            clicker.return_home()
            logger.info(f"RaidRiver Finish")

        if run_param["RaidDark"]:
            logger.info(f"RaidDark Start")
            clicker.click_rate(0.9, 0.2)
            clicker.ocr_click("内海")
            clicker.ocr_click("浊暗之阱")
            clicker.ocr_click("浊暗")
            clicker.ocr_click("扫荡")
            clicker.click_blink()
            clicker.return_home()
            logger.info(f"RaidDark Finish")

        logger.info(f"{self.name} Finish")
        return True

    def stop(self) -> None:

        pass
