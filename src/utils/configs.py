import json
import os
import time

# 动态参数
## 常用参数
curr_dir = os.getcwd()
default_threshold = 0.85
## 环境参数

adb_dir = os.path.join(curr_dir, "assets", "adb", "adb.exe")
scrn_dir = os.path.join(curr_dir, "screenshot.png")  # 截图后用于识别
## 当前日期
formatted_today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
#! 以上参数在引用时需要使用类似config.ocr_dir的格式


# 从Config取值，当前程序专用
def load_config():
    with open(
        os.path.join(curr_dir, "assets", "config", "config.json"), "r", encoding="utf-8"
    ) as f:
        config = json.load(f)
    return config


def save_config():
    with open(
        os.path.join(curr_dir, "assets", "config", "config.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(config, f)


config = load_config()


class cfg:
    adb_dir = adb_dir
    scrn_dir = scrn_dir
    formatted_today = formatted_today
    curr_dir = os.getcwd()
    tool_kit_option = os.path.join(curr_dir, "assets")
    width = 1280
    height = 720
    sleep_time = config["sleep_time"]
