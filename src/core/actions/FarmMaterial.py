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
# 全部比例坐标来自 docs/nav_probe/(2026-09-12 真机探测)
CRISIS_MANAGE = (0.74, 0.89)      # 主界面 -> 危机管理(固定坐标兜底)
CRISIS_MANAGE_TEXT = "危机管理"        # 优先按文本点击(主界面可能被活动弹窗盖住)
DIST_CITY = "狄斯城"               # 关卡选择界面底部模式标签(0.481,0.885); 已在该页时再点无害
CHAPTER_ENTER = (0.80, 0.65)      # 点开章节节点后的详情面板里, 再点标题区进入关卡列表
DIAL_DRAG_UP = ([0.032, 0.60, 10, 10], [0.032, 0.30, 10, 10], 0.8)     # 旋盘推进
DIAL_DRAG_DOWN = ([0.032, 0.30, 10, 10], [0.032, 0.60, 10, 10], 0.8)   # 旋盘回退
STAGE_LIST_SWIPE = ([0.80, 0.59, 10, 10], [0.30, 0.59, 10, 10], 0.8)   # 关卡列表横向滑动
MAX_DIAL_DRAGS = 10               # 旋盘最多拖动次数(章节可能跨多个主线位置)
MAX_LIST_SWIPES = 8               # 关卡列表最多滑动次数(单章最多 18 关)
# 扫荡流程按钮文本(与 Raid.py 的资源关一致)
SWEEP_ENTRY = "连续扫荡"
START_SWEEP = "开始扫荡"
DONE = "完成"
CANCEL = "取消"
# 次数设置(弹窗「米诺斯管理系统-体力消耗」, 坐标来自探测, 与资源关同一套 UI)
# 滑条范围 1..5, 两端为 -/+ 按钮; 次数显示在「选择次数」右侧(OCR 常合并成 选择次数3)
SWEEP_PLUS = (0.7164, 0.6458)
SWEEP_MINUS = (0.2875, 0.6458)
SWEEP_COUNT_ROI = [0.25, 0.565, 0.15, 0.07]
# 弹窗滑条右端值受当前体力限制(探测时为 5), 不是游戏硬上限:
# 因此界面允许填 1..20, 实际能加到哪里由弹窗决定, 加不动就按当前次数继续。
SWEEP_MAX = 20
# 迪斯城地图上才会出现的文本(用于确认真的进了地图)
MAP_MARKERS = ("历史模式", "特别行动", "内海", "锈河", "全天开放")
# 会盖住主界面的面板/页面文本(命中就先退掉)
OVERLAY_MARKERS = ("局长信息", "生涯", "称号", "头像框")  # 注意: 禁闭者/管理局 是主界面按钮, 不能放进来
# 主线导航常量是否可用(探测已完成)
NAV_READY = True


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
        """在迪斯城地图上找「章节节点 + 进度」这一对文本(如 N7 与 1/6), 拼成 N7-1/6"""
        if not NAV_READY:
            return ""
        if not self._open_map(clicker):
            return ""
        items = self._screen_items(clicker)
        fractions = [
            (text.replace(" ", ""), box)
            for text, _score, box in items
            if re.match(r"^\d+/\d+$", text.replace(" ", ""))
        ]
        for frac_text, frac_box in fractions:
            best, best_x = None, -1
            for text, _score, box in items:
                token = text.replace(" ", "")
                # 章节节点在进度文本左侧且同一行
                if (
                    re.match(r"^N?\d+$", token)
                    and box[0] < frac_box[0]
                    and abs(box[1] - frac_box[1]) < 40
                    and box[0] > best_x
                ):
                    best, best_x = token, box[0]
            if best:
                logger.info(f"材料刷取: 地图进度 {best}-{frac_text}")
                return f"{best}-{frac_text}"
        logger.warning("材料刷取: 未在地图上识别到主线进度")
        return ""

    # ------------------------------------------------------------ 导航
    def _screen_items(self, clicker, sleep_time=0.4) -> list:
        """当前屏幕 OCR 结果 [(text, score, box)]"""
        return clicker.ocr_roi([0, 0, 1, 1], sleep_time=sleep_time) or []

    def _screen_texts(self, clicker, sleep_time=0.4) -> list:
        return [t.replace(" ", "") for t, _s, _b in self._screen_items(clicker, sleep_time)]

    def _click_text(self, clicker, text) -> bool:
        """点击屏幕上与 text 完全相同的文本块; 找不到返回 False

        注意 clicker.ocr_click 是子串匹配(MaaFramework 的 expected): 点 "13" 会命中
        "10:30:00" 这类文本; 所以这里先全屏 OCR 做精确匹配, 再点该文本框中心。
        """
        target = str(text).replace(" ", "")
        for screen_text, _score, box in self._screen_items(clicker):
            if screen_text.replace(" ", "") == target:
                x = (box[0] + box[2] / 2) / cfg.width
                y = (box[1] + box[3] / 2) / cfg.height
                logger.debug(f"材料刷取: 点击 {target} @ ({x:.3f},{y:.3f})")
                clicker.click_rate(x, y)
                return True
        return False

    def _open_map(self, clicker) -> bool:
        """回到迪斯城地图(关卡选择界面的主线条目); 返回是否确认在地图上

        每轮先看屏幕再决定动作: 已在目标界面 -> 返回; 有遮挡面板(局长信息等) -> 退掉;
        主界面 -> 点「危机管理」(优先按文本, 找不到用固定坐标); 其它页面 -> 退一层。
        """
        clicker.check_return_home()
        for _ in range(6):
            texts = self._screen_texts(clicker)
            if any(marker in texts for marker in MAP_MARKERS):
                if self._click_text(clicker, DIST_CITY):   # 确保在主线(狄斯城)标签
                    stop_sleep(1.0)
                return True
            if any(marker in texts for marker in OVERLAY_MARKERS):
                logger.info("材料刷取: 关闭遮挡面板")
                clicker.back()
            elif CRISIS_MANAGE_TEXT in texts:
                self._click_text(clicker, CRISIS_MANAGE_TEXT)
            else:
                logger.info("材料刷取: 当前不在主界面, 退一层: " + " | ".join(texts[:8]))
                clicker.back()
            stop_sleep(1.5)
        logger.warning(
            "材料刷取: 未能进入迪斯城地图; 当前屏幕: "
            + " | ".join(self._screen_texts(clicker)[:15])
        )
        return False

    def _goto_chapter(self, clicker, chapter) -> bool:
        """在地图上找到目标章节节点并点开; 不可见时按方向拖旋盘(search by drag)"""
        if self._click_text(clicker, chapter):
            return True
        target = int(re.sub(r"\D", "", chapter) or 0)
        texts = self._screen_texts(clicker)
        logger.info("材料刷取: 地图可见 " + " ".join(texts[:15]))
        for _ in range(MAX_DIAL_DRAGS):
            visible = [
                int(re.sub(r"\D", "", text))
                for text in self._screen_texts(clicker)
                if re.match(r"^N?\d+$", text)
            ]
            # 目标比可见的最新章节还新 -> 推进, 否则回退
            advance = target > max(visible or [0])
            drag = DIAL_DRAG_UP if advance else DIAL_DRAG_DOWN
            logger.info(
                f"材料刷取: 地图未见 {chapter}(可见章节 {sorted(visible)}), "
                f"拖旋盘{'推进' if advance else '回退'}"
            )
            clicker.swape(drag[0], drag[1], drag[2])
            stop_sleep(1.2)
            if self._click_text(clicker, chapter):
                return True
        logger.warning(
            f"材料刷取: 地图上未能找到章节 {chapter}; 当前屏幕: "
            + " | ".join(self._screen_texts(clicker)[:15])
        )
        return False

    def _select_stage(self, clicker, stage) -> bool:
        """在章节关卡列表里选中目标关卡(游戏内编号与 wiki 一致, 如 N7-1)"""
        for _ in range(MAX_LIST_SWIPES + 1):
            if self._click_text(clicker, stage["code"]):
                return True
            clicker.swape(STAGE_LIST_SWIPE[0], STAGE_LIST_SWIPE[1], STAGE_LIST_SWIPE[2])
            stop_sleep(1.0)
        logger.warning(
            f"材料刷取: 关卡列表里未找到 {stage['code']}; 当前屏幕: "
            + " | ".join(self._screen_texts(clicker)[:15])
        )
        return False

    def _farm_one(self, clicker, stage) -> str:
        """扫荡单个关卡; 返回 "ok" / "no_stamina" / "unavailable" """
        if not self._open_map(clicker):
            return "unavailable"
        if not self._goto_chapter(clicker, stage["chapter"]):
            clicker.return_home()
            return "unavailable"
        clicker.click_rate(*CHAPTER_ENTER)          # 章节详情面板 -> 关卡列表
        stop_sleep(1.0)
        if not self._select_stage(clicker, stage):
            clicker.return_home()
            return "unavailable"
        if not self._click_text(clicker, SWEEP_ENTRY):
            clicker.return_home()
            return "unavailable"
        detail = clicker.ocr_click(CANCEL)          # 体力不足会弹取消
        if detail and detail.status.succeeded:
            clicker.click_blink()
            clicker.return_home()
            return "no_stamina"
        if not self._set_sweep_count(clicker, self.param["sweep_count"]):
            clicker.back()
            clicker.return_home()
            return "no_stamina"
        if not self._click_text(clicker, START_SWEEP):
            clicker.back()
            clicker.return_home()
            return "unavailable"
        stop_sleep(12)
        clicker.click_rate(0.5, 0.1)                # 升级弹窗
        self._click_text(clicker, DONE)
        clicker.return_home()
        return "ok"

    def _set_sweep_count(self, clicker, target: int) -> bool:
        """把滑条次数调到目标值(滑条右端受体力限制, 加不动就按当前次数继续)

        读不到次数(界面差异)或怎么点都不动时不当作体力不足, 告警后按当前次数继续 ——
        体力不足由弹窗自身与「开始扫荡」失败暴露, 避免坐标误差导致提前停机。
        """
        target = max(1, min(int(target), SWEEP_MAX))
        current = self._read_sweep_count(clicker)
        if current is None:
            logger.warning("材料刷取: 未读到扫荡次数, 按界面当前次数继续")
            return True
        stall = 0
        while current < target:
            clicker.click_rate(*SWEEP_PLUS)
            stop_sleep(0.5)
            new = self._read_sweep_count(clicker)
            if new is None or new <= current:
                stall += 1
                if stall >= 3:
                    logger.warning(
                        f"材料刷取: 次数未能从 {current} 加到 {target}, 按当前次数继续"
                    )
                    return True
            else:
                stall = 0
                current = new
        return True

    def _read_sweep_count(self, clicker):
        """读弹窗里的次数; OCR 常把标签与数值合并成「选择次数3」"""
        items = clicker.ocr_roi(SWEEP_COUNT_ROI, sleep_time=0.3) or []
        for text, _score, _box in items:
            if "选择次数" in text.replace(" ", ""):
                digits = re.findall(r"\d+", text)
                if digits:
                    return int(digits[-1])
        for text, _score, _box in items:
            digits = re.findall(r"\d+", text)
            if digits:
                return int(digits[-1])
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
