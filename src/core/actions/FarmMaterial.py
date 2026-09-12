# -*- coding: utf-8 -*-
"""材料刷取: 按材料自动刷主线关卡(连续扫荡)

规则与数据见 docs/superpowers/specs/2026-09-12-material-farming-design.md
导航坐标: 已确认的沿用 Raid.py; 主线特有的(旋盘/主线位置/次数区域)需 Task 1 探测后填入,
未就绪时 NAV_READY 保持 False, 任务只记日志不点击。
"""
import json
import re

from loguru import logger
from maa.context import Context

from src.core.TaskerManager import TASKER_MANAGER, MyCustomAction
from src.utils.click import Click, stop_sleep
from src.utils.configs import cfg, save_confg
from src.utils.material_data import (
    MAX_CANDIDATES,
    load_material_data,
    plan,
    progress_key,
)
from src.utils.model import StopException

name = __file__.split("\\")[-1].split(".")[0]

# ---------------------------------------------------------------- 导航常量
# 危机管理入口(与 Raid.py 一致, 已验证)
CRISIS_MANAGE = (0.74, 0.89)
# 入口识别文本
MAIN_STORY = "主线"
DIST_CITY = "迪斯城"
# 扫荡流程按钮文本
SWEEP_ENTRY = "连续扫荡"
START_SWEEP = "开始扫荡"
DONE = "完成"
CANCEL = "取消"
# 次数设置(先用资源关坐标; 主线若不同, 由探测结果替换)
SWEEP_PLUS = (0.7164, 0.6458)
SWEEP_MINUS = (0.2875, 0.6458)
SWEEP_COUNT_ROI = [0.25, 0.588, 0.1, 0.04]
# 旋盘(切换主线位置)与"主线位置 -> 章节"映射: 待探测(docs/nav_probe/coords.md)
REGION_DIAL = None          # 旋盘中心比例坐标 (x, y)
REGION_DRAG_UP = None       # 推进: (start, end, duration)
REGION_DRAG_DOWN = None     # 回退: (start, end, duration)
REGION_CHAPTERS = {}        # {"N10": "新城", "13": "里湾", ...}
# 主线导航是否已具备可用常量(Task 1 探测完成后置 True)
NAV_READY = False


@TASKER_MANAGER.add_action(name)
class FarmMaterial(MyCustomAction):

    def run(self, context: Context, argv: MyCustomAction.RunArg) -> bool:
        self.param = self._load_param(argv.custom_action_param)
        if not self.param["materials"]:
            logger.info("材料刷取: 未选择材料,跳过")
            return True

        clicker = Click(context)
        data = load_material_data()
        progress = self._resolve_progress(clicker)
        key = progress_key(progress)

        remaining = self._load_remaining() or list(self.param["materials"])
        if self._load_remaining():
            logger.info(f"材料刷取: 恢复上次剩余材料: {', '.join(remaining)}")
        if not remaining:
            logger.info("材料刷取: 无待刷材料,跳过")
            return True
        if not NAV_READY:
            logger.error("材料刷取: 主线导航坐标尚未探测(见 docs/nav_probe/coords.md), 本次跳过")
            return True

        plans = plan(data, remaining, key)
        pending: list = []
        try:
            for index, mat in enumerate(remaining):
                entry = plans.get(mat) or {"stage": None, "fallbacks": [], "rejected": []}
                if entry["stage"] is None:
                    logger.warning(f"材料刷取: {mat} 无可用关卡(进度不足),跳过")
                    pending.append(mat)
                    continue
                chain = ([entry["stage"]] + entry["fallbacks"])[:MAX_CANDIDATES]
                logger.info("材料刷取: " + mat + " 候选 " + " -> ".join(s["code"] for s in chain))
                result = "unavailable"
                for stage in chain:
                    stamina = f"体力{stage['stamina']}" if stage.get("stamina") else "体力未知"
                    logger.info(f"材料刷取: {mat} -> {stage['code']} {stage['name']}({stamina})")
                    result = self._farm_one(clicker, stage)
                    if result != "unavailable":
                        break
                    logger.warning(f"材料刷取: {stage['code']} 不可用, 回退下一个候选")
                if result == "ok":
                    continue
                pending.append(mat)
                if result == "no_stamina":
                    pending += remaining[index + 1:]
                    break
        except StopException:
            pending += remaining[index:]  # 当前及之后都算未完成
            self._save_remaining(pending)
            raise
        if pending:
            self._save_remaining(pending)
        else:
            self._clear_remaining()
        logger.info("材料刷取: 完成")
        return True

    # ------------------------------------------------------------ 参数
    @staticmethod
    def _to_dict(raw) -> dict:
        """框架传入的是 JSON 字符串(可能被再编码一层), 也可能已是 dict

        与 Raid._to_dict 同款: maa 的 RunArg.custom_action_param 声明为 str。
        """
        value = raw
        for _ in range(3):
            if isinstance(value, dict):
                return value
            if not isinstance(value, str) or not value:
                break
            try:
                value = json.loads(value)
            except ValueError:
                break
        if raw not in (None, ""):
            logger.warning(f"材料刷取: 参数无法解析: {raw!r}")
        return {}

    def _load_param(self, raw) -> dict:
        """键形如 <材料名>checkBox / SweepCountCombo / ProgressModeCombo / ProgressCombo"""
        param = self._to_dict(raw)
        materials = [
            key[: -len("checkBox")]
            for key, value in param.items()
            if key.endswith("checkBox") and value
        ]
        try:
            count = int(param.get("SweepCountCombo", "3"))
        except (TypeError, ValueError):
            count = 3
        return {
            "materials": materials,
            "sweep_count": max(1, min(count, 20)),
            "progress_mode": param.get("ProgressModeCombo", "自动"),
            "progress_manual": param.get("ProgressCombo", "13"),
        }

    # ------------------------------------------------------------ 进度
    def _resolve_progress(self, clicker) -> str:
        """spec 5.1: 手动 > 本次探测 > 缓存 > 默认 13"""
        if self.param["progress_mode"] == "手动":
            return self.param["progress_manual"] or "13"
        detected = self._detect_progress(clicker)
        if detected:
            cfg.main_progress = detected
            save_confg()
            logger.info(f"材料刷取: 探测到主线进度 {detected}")
            return detected
        if cfg.main_progress:
            logger.info(f"材料刷取: 探测失败, 使用缓存进度 {cfg.main_progress}")
            return cfg.main_progress
        logger.warning("材料刷取: 探测失败且无缓存, 按默认第13章处理")
        return "13"

    def _detect_progress(self, clicker) -> str:
        """进主线界面 OCR 进度文本(形如 N10-3/9 或 N7), 失败返回空串"""
        if not NAV_READY:
            return ""
        clicker.check_return_home()
        clicker.click_rate(*CRISIS_MANAGE)
        self._click_retry(clicker, MAIN_STORY)
        self._click_retry(clicker, DIST_CITY)
        found = []
        for text in clicker.ocr(0.4) or {}:
            cleaned = text.replace(" ", "")
            if re.match(r"^N?\d+(-\d+/\d+)?$", cleaned):
                found.append(cleaned)
        if not found:
            logger.warning("材料刷取: 未识别到主线进度")
            return ""
        return max(found, key=progress_key)

    # ------------------------------------------------------------ 执行
    @staticmethod
    def _click_retry(clicker, text, times=2):
        """OCR 点击失败重试(spec 8)"""
        for _ in range(times):
            detail = clicker.ocr_click(text)
            if detail and detail.status.succeeded:
                return detail
        return None

    def _farm_one(self, clicker, stage) -> str:
        """扫荡单个关卡; 返回 "ok" / "no_stamina" / "unavailable" """
        clicker.check_return_home()
        clicker.click_rate(*CRISIS_MANAGE)
        self._click_retry(clicker, MAIN_STORY)
        self._click_retry(clicker, DIST_CITY)
        if not self._switch_region(clicker, stage):
            clicker.return_home()
            return "unavailable"
        self._click_retry(clicker, stage["chapter"])       # 章节节点
        if not self._click_retry(clicker, stage["name"]):  # 关卡
            clicker.return_home()
            return "unavailable"
        if not self._click_retry(clicker, SWEEP_ENTRY):
            clicker.return_home()
            return "unavailable"
        detail = clicker.ocr_click(CANCEL)                 # 体力不足会弹取消
        if detail and detail.status.succeeded:
            clicker.click_blink()
            clicker.return_home()
            return "no_stamina"
        if not self._set_sweep_count(clicker, self.param["sweep_count"]):
            clicker.back()
            clicker.return_home()
            return "no_stamina"
        if not self._click_retry(clicker, START_SWEEP):
            clicker.back()
            clicker.return_home()
            return "unavailable"
        stop_sleep(12)
        clicker.click_rate(0.5, 0.1)                       # 升级弹窗
        self._click_retry(clicker, DONE)
        clicker.return_home()
        return "ok"

    def _switch_region(self, clicker, stage) -> bool:
        """把主线位置切到目标章节所在的位置(旋盘拖拽); 未探测到映射时返回 False"""
        if not NAV_READY:
            return False
        region = REGION_CHAPTERS.get(stage["chapter"])
        if region is None:
            logger.warning(f"材料刷取: 未探测到 {stage['chapter']} 所属主线位置")
            return False
        # 当前位置由 OCR 判断; 目标在下方则回退, 在上方则推进
        current = None
        for text in clicker.ocr(0.4) or {}:
            if text in REGION_CHAPTERS.values():
                current = text
                break
        if current is None:
            logger.warning("材料刷取: 无法判断当前主线位置, 切换失败")
            return False
        order = list(dict.fromkeys(REGION_CHAPTERS.values()))
        if current == region:
            return True
        if current not in order or region not in order:
            return False
        drag = REGION_DRAG_UP if order.index(region) > order.index(current) else REGION_DRAG_DOWN
        for _ in range(abs(order.index(region) - order.index(current))):
            clicker.swape(drag[0], drag[1], drag[2])
            stop_sleep(1)
        return True

    def _set_sweep_count(self, clicker, target: int) -> bool:
        """点加号设次数; 连续两次无法增加判定体力不足, 返回 False"""
        target = max(1, min(int(target), 20))
        current = self._read_sweep_count(clicker)
        stall = 0
        while current is None or current < target:
            clicker.click_rate(*SWEEP_PLUS)
            stop_sleep(0.6)
            new = self._read_sweep_count(clicker)
            if new is None or (current is not None and new <= current):
                stall += 1
                if stall >= 2:
                    logger.warning(f"材料刷取: 次数无法增加到{target}(当前{current}), 判定体力不足")
                    return False
            else:
                stall = 0
                current = new
        return True

    def _read_sweep_count(self, clicker):
        for text, _score, _box in clicker.ocr_roi(SWEEP_COUNT_ROI, sleep_time=0.3) or []:
            match = re.search(r"(\d+)", text)
            if match:
                return int(match.group(1))
        return None

    # ------------------------------------------------------------ 续刷
    def _save_remaining(self, items) -> None:
        cfg.material_remaining = {"date": cfg.formatted_today, "items": list(items)}
        save_confg()
        logger.warning(f"材料刷取: 记录剩余任务: {', '.join(items)}")

    def _clear_remaining(self) -> None:
        cfg.material_remaining = {"date": "", "items": []}
        save_confg()

    def _load_remaining(self) -> list:
        data = cfg.material_remaining or {}
        if data.get("date") == cfg.formatted_today and data.get("items"):
            return list(data["items"])
        return []

    def stop(self) -> None:
        pass
