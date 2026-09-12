import ctypes
import sys
from ctypes import wintypes

ATTACH_PARENT_PROCESS = -1
TH32CS_SNAPPROCESS = 0x00000002
# 向上查找祖先进程的最大层数
MAX_ANCESTOR_DEPTH = 8


class _PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", ctypes.c_long),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", ctypes.c_char * 260),
    ]


def console_encoding(codepage=None) -> str:
    """控制台输出编码:与控制台代码页一致,避免中文乱码"""
    if codepage is None:
        try:
            codepage = ctypes.windll.kernel32.GetConsoleOutputCP()
        except Exception:
            codepage = 0
    return f"cp{codepage}" if codepage else "cp65001"


def _process_map() -> dict:
    """pid -> 父pid"""
    k32 = ctypes.windll.kernel32
    snapshot = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    entry = _PROCESSENTRY32()
    entry.dwSize = ctypes.sizeof(_PROCESSENTRY32)
    mapping = {}
    if snapshot and k32.Process32First(snapshot, ctypes.byref(entry)):
        while True:
            mapping[int(entry.th32ProcessID)] = int(entry.th32ParentProcessID)
            if not k32.Process32Next(snapshot, ctypes.byref(entry)):
                break
    if snapshot:
        k32.CloseHandle(snapshot)
    return mapping


def _iter_ancestor_pids(limit: int = MAX_ANCESTOR_DEPTH) -> list:
    """由近及远返回祖先进程PID(不含自己)"""
    try:
        import os

        mapping = _process_map()
        current = os.getpid()
        chain = []
        for _ in range(limit):
            parent = mapping.get(current, 0)
            if not parent or parent == current or parent in chain:
                break
            chain.append(parent)
            current = parent
        return chain
    except Exception:
        return []


def _console_candidate_pids() -> list:
    """可能持有控制台的候选进程:父进程 → 祖父进程 → …

    PyInstaller onefile 下,真正执行代码的是 bootloader 派生出的子进程,
    其父进程是没有控制台的 bootloader,因此必须继续向上找到用户的终端。
    """
    return _iter_ancestor_pids()


def _has_console_streams() -> bool:
    """stdout/stderr 是否已可用(源码运行或控制台程序)"""
    for stream in (sys.stdout, sys.stderr):
        try:
            if stream is not None and stream.fileno() >= 0:
                return True
        except Exception:
            continue
    return False


def _bind_console_streams() -> bool:
    """把 stdout/stderr 接到当前控制台"""
    encoding = console_encoding()
    sys.stdout = open("CONOUT$", "w", encoding=encoding, errors="replace", buffering=1)
    sys.stderr = open("CONOUT$", "w", encoding=encoding, errors="replace", buffering=1)
    return True


def attach_parent_console() -> bool:
    """确保有可写的控制台输出,返回是否可用

    - 源码运行/控制台程序: 直接可用
    - --noconsole 打包后从终端启动: 沿祖先进程链找到持有控制台的进程并接管
    - 双击启动(链上没有控制台): 不接管、不额外弹窗,返回 False
    """
    if _has_console_streams():
        return True
    if not hasattr(ctypes, "windll"):
        return False
    candidates = _console_candidate_pids() or [ATTACH_PARENT_PROCESS]
    for pid in candidates:
        try:
            if not ctypes.windll.kernel32.AttachConsole(pid):
                continue
            return _bind_console_streams()
        except Exception:
            continue
    return False
