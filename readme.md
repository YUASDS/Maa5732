# MAA5732

<div><p align="center">
<img src="src/ui/logo.ico" /></p></div>

Base on [MaaFramwork](https://github.com/MaaXYZ/MaaFramework)
部分代码参考了 [MaaYYS](https://github.com/TanyaShue/MaaYYs)图标来源于网络，如有侵权，请联系删除。
<!-- markdownlint-disable MD033 MD041 -->
<div align="center">
<img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" alt="Python" /><a href="https://github.com/YUASDS/Maa5732/blob/main/LICENSE"><img src="https://img.shields.io/github/license/YUASDS/Maa5732" alt="Licence" /></a>
<p align="center">
<img src="https://count.getloli.com/get/@YUASDS-Maa5732?theme=rule34" alt="访问次数" /></p></div>

## 计划功能

- [ ] 定时启动游戏
- [x] 完成登录及签到月卡
- [x] 工会捐赠(基本完成)
- [x] 采购办免费体力
- [ ] 采购办友情点商店
- [ ] 采购办活动商店
- [x] 邮件领取
- [x] 基建收菜
- [x] 管理局体力
- [x] 管理局派遣
- [x] 赠送/收取友情点
- [ ] 自动点赞
- [x] 深井扫荡
- [x] 锈河扫荡
- [x] 监察密令领取
- [ ] 自动切换扫荡队伍

## 使用方法

- 下载Release,解压并运行MAA_5732.exe即可
- 启动功能可直接启动游戏，基本稳定
- 其他功能的需要在游戏主界面开始
- 目前能完成游戏中的大部分日常

### 刷材料（主线）

在「刷材料」页勾选需要的紫阶材料（裂生冰晶锥、异化尖刺骨片等 12 种），程序会按你的主线进度
自动选择掉落该材料的关卡并连续扫荡；勾选后页面下方会直接显示「将刷」的关卡，方便核对。

- **主线进度**：默认每次任务开始时自动探测（在主线界面读取形如 `N7-1/6` 的进度），也可以在该页
  手动指定章节；探测失败会用上次缓存，都没有则按第 13 章处理
- **选关规则**：候选关卡按主线顺序（N 系列 > 第 13 章 > … > 第 1 章）从新到旧排列，取进度内最新的
  那一关；该关不可扫荡时自动回退到下一个候选
- **次数与体力**：每关默认扫荡 3 次（可改）；体力不足会自动停止，并把剩余材料记下来，
  当天再次运行会继续刷剩下的
- 材料数据与图标由 `tools/build_material_data.py` 从 `docs/wiki/` 的 wiki 快照离线生成，
  wiki 更新后重跑该脚本即可

## 从源码运行

```bash
pip install -r requirements.txt
python main.py
```

`assets/` 中只有模板图、`assets/ui` 图标等必需资源纳入版本控制，以下资源需要自行准备（Release 压缩包中已包含）：

- `assets/adb/adb.exe`：自带adb，缺失时回退使用系统PATH中的adb
- `assets/resource/model/ocr/`：OCR模型(det.onnx / rec.onnx / keys.txt)
- `assets/MaaCommonAssets/`：可选，MaaFramework公共资源

首次运行会自动生成 `assets/config/config.json`；该文件是运行时配置，不纳入版本控制。

## 日志

- 日志同时写入 `logs/`（保留最近7天）和运行终端
- **在终端里运行**（源码 `python main.py`，或 `MAA_5732_x.y.z.exe`）会直接在当前终端输出日志；双击启动则不显示控制台窗口
- 注意：exe 是窗口程序，终端不会等待它结束，提示符会立刻返回，日志随后异步打印在该终端里；需要阻塞等待可用 `start /wait MAA_5732_x.y.z.exe`
- 终端默认输出 INFO 级别，需要更详细(排查问题)时可以：

```bat
set MAA5732_LOG_LEVEL=DEBUG
MAA_5732_0.2.3.exe
```

## 打包

```bash
python build.py
```

生成的 `MAA_5732_x.y.z.exe` 与 `MAA_5732_x.y.z.zip` 位于 `dist/`。
