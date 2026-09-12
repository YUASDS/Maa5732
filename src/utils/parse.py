from src.utils.configs import PIPELINE_ORDER


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


def json2pipline(data: list[dict]) -> dict:
    """把界面状态转换为MaaFramework流水线

    data[0] 为各任务开关,data[1] 为各任务的详细设置。
    未勾选的任务替换为 Nothing;详细设置作为 custom_action_param 的
    JSON对象直接写入(与框架的 json::value 参数一致,动作侧自行解析)。
    """
    toggles = data[0] if data else {}
    details = data[1] if len(data) > 1 else {}
    pipeline = {}
    for node_id, action, next_node in PIPELINE_ORDER:
        if toggles.get(action):
            node = {"action": "custom", "custom_action": action}
            param = details.get(action)
            if isinstance(param, dict):
                node["custom_action_param"] = dict(param)
        else:
            node = {"action": "custom", "custom_action": "Nothing"}
        if next_node is not None:
            node["next"] = next_node
        pipeline[node_id] = node
    return pipeline
