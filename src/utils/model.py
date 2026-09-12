class StopException(Exception):
    pass


class DeviceNotFoundError(Exception):
    """等待ADB设备超时,未找到可用设备"""
