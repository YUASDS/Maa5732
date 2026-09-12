import os
import site
import shutil
import zipfile
from pathlib import Path

import PyInstaller.__main__

from src.core import version

# 项目根目录(脚本所在目录),不依赖工作目录
current_dir = str(Path(__file__).resolve().parent)


def find_in_site_packages(*parts: str):
    """在 site-packages 中查找指定子目录,找不到返回None"""
    for path in site.getsitepackages():
        potential_path = os.path.join(path, *parts)
        if os.path.exists(potential_path):
            return potential_path
    return None


# 查找包含 maa/bin 的路径
maa_bin_path = find_in_site_packages("maa", "bin")
if maa_bin_path is None:
    raise FileNotFoundError("Path containing maa/bin not found")

# 查找包含 MaaAgentBinary 的路径
maa_bin_path2 = find_in_site_packages("MaaAgentBinary")
if maa_bin_path2 is None:
    raise FileNotFoundError("Path containing MaaAgentBinary not found")

# 构建 --add-data 参数
add_data_param = f"{maa_bin_path}{os.pathsep}maa/bin"
add_data_param2 = f"{maa_bin_path2}{os.pathsep}MaaAgentBinary"

# 运行 PyInstaller 打包命令
PyInstaller.__main__.run(
    [
        os.path.join(current_dir, "main.py"),
        "--onefile",
        f"--name=MAA_5732_{version}.exe",
        f"--add-data={add_data_param}",
        f"--add-data={add_data_param2}",
        f"--distpath={os.path.join(current_dir, 'dist')}",
        f"--workpath={os.path.join(current_dir, 'build')}",
        f"--specpath={current_dir}",
        "--clean",
        "--uac-admin",
        f"--icon={os.path.join(current_dir, 'src', 'ui', 'logo.ico')}",
        "--noconsole",
    ]
)


# 复制 assets 文件夹到 dist 目录
dist_dir = os.path.join(current_dir, "dist")
assets_source_path = os.path.join(current_dir, "assets")
assets_dest_path = os.path.join(dist_dir, "assets")

if not os.path.exists(assets_source_path):
    raise FileNotFoundError("assets folder not found")

# 如果目标路径存在，先删除它
if os.path.exists(assets_dest_path):
    shutil.rmtree(assets_dest_path)

# 使用 shutil 复制整个文件夹
shutil.copytree(assets_source_path, assets_dest_path)

# 压缩 dist 文件夹为 zip 文件，并保存在 dist 目录中
zip_filename = f"MAA_5732_{version}.zip"
zip_filepath = os.path.join(dist_dir, zip_filename)

with zipfile.ZipFile(zip_filepath, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(dist_dir):
        for file in files:
            # 获取文件的绝对路径并相对路径
            file_path = os.path.join(root, file)
            # 跳过刚生成的压缩包
            if file == zip_filename:
                continue
            arcname = os.path.relpath(file_path, dist_dir)
            zipf.write(file_path, arcname)

print(f"Packaging and compression completed: {zip_filepath}")
