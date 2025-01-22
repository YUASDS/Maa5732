import json

from src.utils.configs import base_template


def parse_screencap_methods(methods):
    """解析截图方法位掩码"""
    available_methods = []
    if methods & 1:
        available_methods.append("adb screencap")
    if methods & 2:
        available_methods.append("minicap")
    if methods & 4:
        available_methods.append("uiautomator")
    return "\n".join(available_methods) if available_methods else "无可用截图方法"


def parse_input_methods(methods):
    """解析输入方法位掩码"""
    available_methods = []
    if methods & 1:
        available_methods.append("adb input")
    if methods & 2:
        available_methods.append("minitouch")
    return "\n".join(available_methods) if available_methods else "无可用输入方法"


def json2pipline(data: list[dict]):
    this_strings = base_template
    for key, value in data[0].items():
        if not value:
            # 将关闭的动作替换为什么都不做
            this_strings = this_strings.replace(key, "Nothing")
        if value and key in data[1]:
            # 将占位的配置替换为实际的配置
            this_strings = this_strings.replace(f'"{key}Custom"', str(data[1][key]))
    # 转换为json字符串
    this_strings = (
        this_strings.replace("'", '"').replace("True", "true").replace("False", "false")
    )
    return json.loads(this_strings)
