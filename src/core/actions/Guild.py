import time

from loguru import logger
from maa.context import Context


from src.utils.configs import cfg
from src.utils.click import Click
from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction


@TASKER_MANAGER.add_action
class Guild(MyCustomAction):
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
        click = Click(context)
        click.click_rate(0.829, 0.911)
        # 左下角秘盟可导致OCR出现问题
        click.click_rate(0.9, 0.3)

        click.click_blink()
        click.ocr_click("秘盟捐赠")
        click.ocr_click("全部", roi=[0, 0, 0.3, 1])
        click.click_blink()
        click.return_home()
        logger.info(f"{self.name} Finish")
        return True

    def stop(self) -> None:

        pass
