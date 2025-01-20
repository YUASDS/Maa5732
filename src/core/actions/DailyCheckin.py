from loguru import logger
from maa.context import Context

from src.utils.configs import cfg
from src.utils.click import Click
from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction


@TASKER_MANAGER.add_action
class DailyCheckin(MyCustomAction):
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
        target, detail = click.click_rate(0.825, 0.15)
        target, detail = click.click_rate(0.807, 0.64)
        # 点击预设
        click.return_home()
        logger.info(f"{self.name} Finish")

        return True

    def stop(self) -> None:
        pass
