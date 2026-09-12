# -*- coding: utf-8 -*-
"""监察密令: 领取每日/每周/密令奖励

**只用 OCR 文本识别, 不使用模板图片** —— 游戏改版后按钮美术变化不影响识别,
因此无需再替换 assets 里的截图模板。

任何一步找不到按钮只记日志并继续, 不中断整条日常流程。
"""
from loguru import logger
from maa.context import Context

from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction
from src.utils.click import Click, stop_sleep
from src.utils.configs import cfg

name = __file__.split("\\")[-1].split(".")[0]

# 主界面入口: 优先按文本(改版只改美术也能识别), 坐标兜底(真机探测)
SUPERVISION_ENTRY_TEXT = "监察密令"
SUPERVISION_ENTRY = (0.941, 0.842)
# 已在监察密令页的标记(出现任一即可)
PAGE_MARKERS = ("监察任务", "奖励预览", "密令装束", "监察兑换")
# 三个奖励标签位于页面左侧竖列, 用 ROI 限位避免「密令」误匹配到「密令装束」「监察密令」
TAB_ROI = [0.28, 0.20, 0.13, 0.40]
REWARD_TABS = ("每日", "每周", "密令")
# 弹窗选项: 未购买高级密令时会问"是否前往购买", 选「直接领取」继续
DIALOG_CHOICES = ("直接领取", "确认", "确定", "领取")
CLAIM_ALL = "一键领取"
CLAIM_ONE = "领取"
# 密令页默认停在等级/奖励视图, 需先切到底部的「监察任务」页才有每日/每周/密令标签
TASK_TAB = "监察任务"


@TASKER_MANAGER.add_action(name)
class Supervision(MyCustomAction):

    def run(self, context: Context, argv) -> bool:
        logger.info("监察密令 开始")
        clicker = Click(context)
        if not self._open_page(clicker):
            logger.warning("监察密令: 未能进入监察密令页面, 跳过本次")
            return True
        # 先切到「监察任务」页(默认停在等级/奖励视图, 那里没有每日/每周标签)
        self._click(clicker, TASK_TAB, retry=2)
        stop_sleep(1.8)
        for tab in REWARD_TABS:
            self._claim_tab(clicker, tab)
        clicker.return_home()
        logger.info("监察密令 结束")
        return True

    # ------------------------------------------------------------ 基础
    @staticmethod
    def _items(clicker, roi=None, sleep_time=0.4) -> list:
        return clicker.ocr_roi(roi or [0, 0, 1, 1], sleep_time=sleep_time) or []

    def _find(self, clicker, text, roi=None, prefix=False, loose=False) -> tuple:
        """返回 (文本, 比例中心坐标); 找不到返回 (None, None)

        文本用「去掉空格后」比较; prefix=True 时允许匹配以目标开头的文本
        (游戏里标签常与角标合并, 如 OCR 读到「每日：24」)。
        """
        target = text.replace(" ", "")
        for item_text, _score, box in self._items(clicker, roi):
            cleaned = item_text.replace(" ", "")
            if cleaned == target or (prefix and cleaned.startswith(target)) or (
                loose and len(cleaned) >= 3 and (cleaned in target or target in cleaned)
            ):
                x = (box[0] + box[2] / 2) / cfg.width
                y = (box[1] + box[3] / 2) / cfg.height
                return cleaned, (x, y)
        return None, None

    def _click(self, clicker, text, roi=None, prefix=False, loose=False, retry=2) -> bool:
        for _ in range(retry):
            found, pos = self._find(clicker, text, roi=roi, prefix=prefix, loose=loose)
            if found:
                logger.debug(f"监察密令: 点击「{found}」@ ({pos[0]:.3f},{pos[1]:.3f})")
                clicker.click_rate(*pos)
                return True
            stop_sleep(0.6)
        visible = [t.replace(" ", "") for t, _s, _b in self._items(clicker)]
        logger.warning(
            f"监察密令: 未找到「{text}」(roi={roi}, prefix={prefix}, loose={loose}); "
            "当前屏幕: " + " | ".join(visible[:20])
        )
        return False

    def _has(self, clicker, markers, roi=None) -> bool:
        texts = [t.replace(" ", "") for t, _s, _b in self._items(clicker, roi)]
        return any(m in texts for m in markers)

    # ------------------------------------------------------------ 流程
    def _open_page(self, clicker) -> bool:
        """进入监察密令页面: 点入口(文本优先, 坐标兜底), 进不去就退一层重试"""
        clicker.check_return_home()
        for _ in range(3):
            if self._has(clicker, PAGE_MARKERS):
                return True
            if not self._click(clicker, SUPERVISION_ENTRY_TEXT, loose=True, retry=1):
                clicker.click_rate(*SUPERVISION_ENTRY)
            stop_sleep(2.5)
            if self._has(clicker, PAGE_MARKERS):
                return True
            clicker.back()
            stop_sleep(1.5)
        return False

    def _claim_tab(self, clicker, tab) -> None:
        logger.info(f"监察密令: 领取「{tab}」")
        if not self._click(clicker, tab, roi=TAB_ROI, prefix=True):
            return
        stop_sleep(1.8)
        self._claim_all(clicker)

    def _claim_all(self, clicker) -> None:
        """一键领取; 没有该按钮时退化为逐个领取"""
        if self._click(clicker, CLAIM_ALL, retry=2):
            stop_sleep(1.8)
            self._dismiss_dialog(clicker)
            clicker.click_rate(0.5, 0.5)      # 奖励展示: 点空白关闭
            stop_sleep(1.0)
            return
        claimed = 0
        for _ in range(6):
            if not self._click(clicker, CLAIM_ONE, retry=1):
                break
            claimed += 1
            stop_sleep(1.2)
            self._dismiss_dialog(clicker)
        if claimed:
            clicker.click_rate(0.5, 0.5)
            stop_sleep(1.0)

    def _dismiss_dialog(self, clicker) -> None:
        """处理「未购买高级监察密令」等弹窗: 选可直接领取的选项"""
        for choice in DIALOG_CHOICES:
            found, pos = self._find(clicker, choice)
            if found:
                logger.info(f"监察密令: 弹窗选择「{found}」")
                clicker.click_rate(*pos)
                stop_sleep(1.5)
                return

    def stop(self) -> None:
        pass
