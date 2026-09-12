import os
import sys


def get_base_dir() -> str:
    """程序根目录:打包后为 exe 所在目录,源码运行为项目根目录"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


BASE_DIR = get_base_dir()
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


def asset_path(*parts: str) -> str:
    """返回 assets 目录下的绝对路径,避免依赖 os.getcwd()"""
    return os.path.join(ASSETS_DIR, *parts)
