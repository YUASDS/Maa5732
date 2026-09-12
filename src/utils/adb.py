import re
import subprocess

# PIPE
from subprocess import DEVNULL, PIPE
from loguru import logger
from src.utils.configs import cfg as cfg

# 常见模拟器ADB端口
EMULATOR_ADDRESSES = [
    "127.0.0.1:16384",  # MuMu模拟器
    "127.0.0.1:16416",
    "127.0.0.1:16448",
    "127.0.0.1:5555",  # 通用/雷电
    "127.0.0.1:5557",
    "127.0.0.1:7555",  # 雷电模拟器
    "127.0.0.1:62001",  # 夜神模拟器
    "127.0.0.1:62025",
    "127.0.0.1:21503",  # 网易MuMu?
]


def adb_run(cmd, **kwargs):
    """运行adb命令,不弹出命令行窗口"""
    kwargs.setdefault("creationflags", subprocess.CREATE_NO_WINDOW)
    return subprocess.run(cmd, **kwargs)


def emulator_alias_port(address: str):
    """emulator-5554 与 127.0.0.1:5555 指向同一设备,返回等价adb端口,非该形式返回None"""
    if not isinstance(address, str) or not address.startswith("emulator-"):
        return None
    try:
        return int(address[len("emulator-"):]) + 1
    except ValueError:
        return None


def same_device(address_a: str, address_b: str) -> bool:
    """两个adb地址是否指向同一设备(兼容 emulator-<n> 与 127.0.0.1:<n+1> 两种写法)"""
    if not address_a or not address_b:
        return False
    if address_a == address_b:
        return True
    port = emulator_alias_port(address_a)
    if port is not None and address_b == f"127.0.0.1:{port}":
        return True
    port = emulator_alias_port(address_b)
    if port is not None and address_a == f"127.0.0.1:{port}":
        return True
    return False


def online_devices():
    """返回 adb devices 中状态为 device 的地址集合

    offline/unauthorized 等不可用状态不计入;查询失败返回 None(调用方据此放弃过滤)。
    """
    try:
        result = adb_run(
            [cfg.adb_dir, "devices"],
            stdout=PIPE,
            stderr=PIPE,
            timeout=10,
        )
    except Exception as e:
        logger.warning(f"查询ADB设备状态失败: {e}")
        return None
    online = set()
    for line in result.stdout.decode(errors="ignore").splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            online.add(parts[0])
    return online


def filter_online_devices(devices: list) -> list:
    """按 adb devices 的真实状态过滤设备列表,查询失败时原样返回(保守处理)"""
    online = online_devices()
    if online is None:
        return list(devices)
    return [
        device
        for device in devices
        if any(same_device(getattr(device, "address", ""), item) for item in online)
    ]


def change_size(adb_adress):
    result = adb_run(
        [cfg.adb_dir, "-s", adb_adress, "shell", "wm", "size"],
        stdout=PIPE,
        stderr=PIPE,
    )
    pat = re.compile(r"\d{1,5}")
    width, height = pat.findall(result.stdout.decode())
    cfg.width, cfg.height = int(width), int(height)


def restart():
    adb_run(
        [cfg.adb_dir, "kill-server"],
        stdout=PIPE,
        stderr=PIPE,
    )
    adb_run(
        [cfg.adb_dir, "start-server"],
        stdout=PIPE,
        stderr=PIPE,
    )


def start_server():
    adb_run(
        [cfg.adb_dir, "start-server"],
        stdout=PIPE,
        stderr=PIPE,
    )


def connect_adb_devices(addresses=None):
    """尝试连接常见模拟器端口及指定地址的ADB设备

    adb connect 对"端口开着但不是可用adb设备"也会返回0并打印connected,
    因此必须用 adb devices 的真实状态复核,只把真正就绪的设备记为已连接。
    """
    targets = list(EMULATOR_ADDRESSES)
    if addresses:
        for address in addresses:
            if address and address not in targets:
                targets.append(address)
    if not targets:
        return
    online_before = online_devices()
    if online_before is None:
        online_before = set()
    claimed = []
    for address in targets:
        if any(same_device(address, item) for item in online_before):
            continue
        try:
            result = adb_run(
                [cfg.adb_dir, "connect", address],
                stdout=PIPE,
                stderr=PIPE,
                timeout=10,
            )
        except Exception:
            continue
        if (
            result.returncode == 0
            and "connected" in result.stdout.decode(errors="ignore")
        ):
            claimed.append(address)
    if not claimed:
        return
    online_after = online_devices()
    if online_after is None:
        online_after = set()
    for address in claimed:
        if any(same_device(address, item) for item in online_after):
            logger.debug(f"ADB设备已连接: {address}")
        else:
            logger.warning(f"ADB端口无响应(不是可用设备,已忽略): {address}")


# 常见模拟器进程名(按优先级)
EMULATOR_PROCESSES = [
    "MuMuVMMHeadless.exe",  # MuMu模拟器虚拟机(核心)
    "MuMuNxMain.exe",       # MuMu模拟器主程序
    "MuMuNxDevice.exe",     # MuMu设备进程
    "MuMuRemoteService.exe",  # MuMu远程服务
    "NoxVMHandle.exe",      # 夜神模拟器
    "LdVBoxHeadless.exe",   # 雷电模拟器
    "HD-Player.exe",        # 蓝叠模拟器
]


def close_emulator():
    """关闭模拟器:结束游戏进程→adb emu kill→结束常见模拟器进程"""
    logger.info("尝试关闭模拟器")
    # 1) 结束本程序启动的游戏/模拟器进程(含子进程树)
    if cfg.game_process and cfg.game_process.poll() is None:
        try:
            result = adb_run(
                ["taskkill", "/F", "/T", "/PID", str(cfg.game_process.pid)],
                stdout=PIPE,
                stderr=PIPE,
            )
            if result.returncode == 0:
                logger.info("已关闭游戏进程")
        except Exception as e:
            logger.warning(f"关闭游戏进程失败: {e}")
    # 2) 尝试 adb emu kill(优先所选设备,再默认端口)
    for address in ([cfg.adb_address] if cfg.adb_address else []) + [None]:
        try:
            cmd = [cfg.adb_dir, "emu", "kill"]
            if address:
                cmd = [cfg.adb_dir, "-s", address, "emu", "kill"]
            result = adb_run(cmd, stdout=PIPE, stderr=PIPE)
            if result.returncode == 0:
                logger.info(f"已发送关闭模拟器指令: {address or '默认'}")
        except Exception as e:
            logger.warning(f"关闭模拟器失败: {e}")
    # 3) 结束常见模拟器进程(MuMu等不响应adb emu kill时的兜底)
    for name in EMULATOR_PROCESSES:
        try:
            result = adb_run(
                ["taskkill", "/F", "/IM", name],
                stdout=PIPE,
                stderr=PIPE,
            )
            if result.returncode == 0:
                logger.info(f"已关闭模拟器进程: {name}")
        except Exception as e:
            logger.warning(f"关闭进程失败 {name}: {e}")
