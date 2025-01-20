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
