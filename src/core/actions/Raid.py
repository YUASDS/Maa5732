import json
import time
from loguru import logger
from maa.context import Context

from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction
from src.utils.configs import cfg
from src.utils.click import Click

default_cfg = {
    "RaidRiver": True,
    "RaidDark": True,
    "ResourceCombo": "狄斯币",
    "ResourceLevelCombo": "4",
    "StromLevelCombo": "5",
}

action_dict = {}


def gold_fight(context: Context):
    clicker = Click(context)
    clicker.click_rate(0.9, 0.2)


name = __file__.split("\\")[-1].split(".")[0]


@TASKER_MANAGER.add_action(name)
class Raid(MyCustomAction):
    action_dict = {
        "狄斯币": ["行动", "狂热"],
        "狂乱精粹": ["行动", "之种"],
        "技能模组": ["污染", "探查"],
        "重构碎片": ["污染", "极域"],
        "异能源质": ["废墟", "异能"],
        "诡秘源质": ["废墟", "诡秘"],
        "坚韧源质": ["废墟", "坚韧"],
        "狂暴源质": ["废墟", "狂暴"],
        "精准源质": ["废墟", "精准"],
        "启迪源质": ["废墟", "启迪"],
    }
    run_param: dict = default_cfg.copy()

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
        action_param = json.loads(argv.custom_action_param)
        run_param = default_cfg.copy()
        if action_param != {}:
            run_param = action_param
            self.run_param = run_param
        clicker = Click(context)
        # 点击危机管理
        self.clicker = clicker
        clicker.click_rate(0.74, 0.89)
        if run_param["RaidRivercheckBox"]:
            self.RaidRiver()
        if run_param["RaidDarkcheckBox"]:
            self.RaidDark()
        if run_param["RaidFightcheckBox"]:
            self.RaidFight()
        logger.info(f"{name} Finish")
        return True

    def RaidDark(self):
        clicker = self.clicker
        logger.info("RaidDark Start")
        # 进入战斗
        clicker.click_rate(0.9, 0.2)
        clicker.ocr_click("内海")
        clicker.swape([0.8, 0.5, 10, 10], [0.1, 0.3, 10, 10], 0.8)
        clicker.ocr_click("浊暗之阱")
        clicker.ocr_click("浊暗", roi=[0.25, 0, 0.75, 1])
        clicker.ocr_click("扫荡")
        clicker.click_blink()
        clicker.return_home()
        logger.info("RaidDark Finish")

    def RaidRiver(self):
        logger.info("RaidRiver Start")
        self.RiverFight("记忆风暴", "点")
        # MS-r5
        logger.info("RaidRiver Finish")

    def RaidFight(self):
        ResourceCombo = self.run_param["ResourceCombo"]
        logger.info(f"RaidFight Start Resource: {ResourceCombo}")
        self.RiverFight(*self.action_dict[ResourceCombo])
        logger.info("RaidFight Finish")

    def RiverFight(self, first_action, second_action):
        # 选择锈河副本 - 第一次点击的文本 第二次点击的文本
        level = self.run_param["ResourceLevelCombo"]
        clicker = self.clicker
        clicker.click_rate(0.9, 0.2)
        clicker.ocr_click("锈河")
        clicker.ocr_click(first_action)
        clicker.ocr_click(second_action)
        if second_action == "极域" and level >= "4":
            level = "3"
        if first_action == "记忆风暴":
            level = self.run_param["StromLevelCombo"]
            if level == "5":
                level = "MS"
                clicker.ocr_click(level, roi=[0, 0.5, 1, 1])
            else:
                clicker.click_rate(0.7, 0.3)
                clicker.ocr_click(level, roi=[0, 0.41, 1, 0.2])
        else:
            clicker.ocr_click(level, roi=[0, 0.5, 1, 1])
        clicker.ocr_click("连续扫荡")
        # 当体力副本无体力时
        detail = clicker.ocr_click("取消")
        if detail and detail.status.succeeded:
            clicker.click_blink()
            clicker.return_home()
            logger.warning("资源不足 取消扫荡")
            return

        clicker.ocr_click("开始扫荡")
        time.sleep(10)
        # 升级的情况
        clicker.click_rate(0.5, 0.1)
        clicker.ocr_click("完成")
        # 继续扫荡
        clicker.ocr_click("连续扫荡")
        # 当体力副本无体力时
        detail = clicker.ocr_click("取消")
        if detail and detail.status.succeeded:
            clicker.click_blink()
            clicker.return_home()
            logger.warning("资源不足 取消扫荡")
            return
        clicker.ocr_click("开始扫荡")
        time.sleep(10)
        # 升级的情况
        clicker.click_rate(0.5, 0.1)
        clicker.ocr_click("完成")
        clicker.return_home()

    def stop(self) -> None:

        pass
