import random
import time
from maa.context import Context
from loguru import logger

from src.utils.configs import cfg


class Click:
    context: Context

    def __init__(self, context: Context) -> None:
        self.context = context

    def trans_from_rate_to_position(self, x, y, offset_x=5, offset_y=5):
        """
        Generate random x and y based on a normal distribution  within +- 12px.
        precondition x !=0.0
        Returns:
            List[float]: A list of generated coordinates [x, y, xx, yy].
        """
        x = round(cfg.width * x, 2)
        y = round(cfg.height * y, 2)
        return [x - offset_x, y - offset_y, offset_x, offset_y]

    def click_rate(self, x, y, offset_x=5, offset_y=5):
        time.sleep(cfg.sleep_time)
        target = self.trans_from_rate_to_position(
            x, y, offset_x=offset_x, offset_y=offset_y
        )
        random_num = random.random()
        detail = self.context.run_task(
            f"just_click_{random_num}",
            {f"just_click_{random_num}": {"action": "Click", "target": target}},
        )
        logger.debug(f"Clicked {target}")
        return (target, detail)

    def ocr_click(self, text, sleep_time=cfg.sleep_time, roi=[0, 0, 0, 0]):
        time.sleep(sleep_time)
        random_num = random.random()
        if roi != [0, 0, 0, 0]:
            roi = [
                roi[0] * cfg.width,
                roi[1] * cfg.height,
                roi[2] * cfg.width,
                roi[3] * cfg.height,
            ]
        logger.debug(f"StartClick: {text}")
        detail = self.context.run_task(
            f"{text}_{random_num}",
            {
                f"{text}_{random_num}": {
                    "timeout": 1500,
                    "recognition": "OCR",
                    "roi": roi,
                    "expected": text,
                    "action": "Click",
                }
            },
        )
        logger.debug(f"Click_{text} Finish")
        return detail

    def return_home(self):
        time.sleep(cfg.sleep_time)
        logger.debug("ReturnHome Start")
        detail = self.click_rate(0.15, 0.1)
        logger.debug("ReturnHome Finish")
        return detail

    def back(self):
        time.sleep(cfg.sleep_time)
        logger.debug("Back Start")
        detail = self.click_rate(0.04, 0.06)
        logger.debug("Back Finish")
        return detail

    def click_blink(self):
        time.sleep(cfg.sleep_time)
        logger.debug("ClickBlink Start")
        detail = self.click_rate(0.6, 0.97)
        logger.debug("ClickBlink Finish")
        return detail

    def swape(self, start, end, duration):
        if start[0] < 1:
            start[0] = start[0] * cfg.width
            start[1] = start[1] * cfg.height
            end[0] = end[0] * cfg.width
            end[1] = end[1] * cfg.height
        time.sleep(cfg.sleep_time)
        random_num = random.random()
        logger.debug(f"StartSwape_{random_num}:{start} {end}")

        detail = self.context.run_task(
            f"Swipe_{random_num}",
            {
                f"Swipe_{random_num}": {
                    "action": "Swipe",
                    "begin": start,
                    "end": end,
                    "duration": duration,
                }
            },
        )
        logger.debug(f"StartSwape_{random_num} Finish")
        return detail

    def check_stage_return_home(self, stage_name):
        time.sleep(cfg.sleep_time)
        logger.debug(f"CheckStage_{stage_name} Start")
        detail = self.ocr_click(stage_name)
        logger.debug(f"CheckStage_{stage_name} Finish")
        return detail

    def ocr_rate_click(
        self,
        text,
        x,
        y,
        offset_x=5,
        offset_y=5,
        sleep_time=cfg.sleep_time,
        roi=[0, 0, 0, 0],
    ):
        time.sleep(sleep_time)
        logger.debug(f"StartSearch: {text}")
        detail = self.context.run_task(
            text,
            {
                text: {
                    "timeout": 1500,
                    "recognition": "OCR",
                    "roi": roi,
                    "expected": text,
                }
            },
        )
        logger.debug(f"Search_{text} Finish")
        if detail and detail.status.succeeded:
            last_detail = self.click_rate(x, y, offset_x, offset_y)
            return last_detail[1]
