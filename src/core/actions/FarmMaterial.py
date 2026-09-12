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
# 原则: 能用 OCR 文本定位的就不写坐标(游戏改版只换美术时依然可用);
# 只有 OCR 认不出的图标(如次数弹窗的 +)才保留坐标, 并注明原因。
CRISIS_MANAGE_TEXT = "危机管理"        # 主界面底部标签: 确保停在能看到进度卡的界面
CARD_FALLBACK_TEXT = "狄斯"            # 进度卡上的地区名(关卡编号正则没匹配到时的兜底)
STAGE_CODE_RE = r"^[A-Za-z]{0,4}N?\d+-\d+$"   # 关卡编号样式, 如 N7-1 / ReN7-2 / 13-8
# 左侧旋盘上的"主线位置"标签(用于定位可拖动的标签)
REGION_LABELS = ("远邦", "新城·1", "新城", "里湾", "狄斯西区", "狄斯东区")
DIST_CITY = "狄斯城"               # 副本界面底部模式标签; 已在该页时再点无害
# 旋盘(切换主线位置): 按住左侧"主线位置标签"拖动才生效 —— 纯竖直滑动游戏不认,
# 必须带一点 x 漂移; duration 单位是毫秒, 实测 1500 有效(参数经真机验证)。
# 行程实测: 0.08 / 0.11 / 0.134(=标签行距) 都能移动一档, >=0.16 会被游戏忽略(拉过头),
# 因此行程在运行时由 OCR 量出的标签行距推算, 不写死。
DIAL_TRAVEL_RATIO = 0.8            # 行程 = 标签行距 × 该系数
DIAL_TRAVEL_MAX = 0.12             # 行程上限(超过游戏会忽略)
DIAL_TRAVEL_MIN = 0.06
DIAL_TRAVEL_FALLBACK = 0.11        # 量不到标签行距时的行程
DIAL_MS = 1500                     # 拖动时长(毫秒)
DIAL_DRIFT_DOWN = -0.003           # 向下拖时的 x 漂移
DIAL_DRIFT_UP = 0.007              # 向上拖时的 x 漂移
DIAL_FALLBACK = (0.079, 0.50)      # 找不到标签时的兜底起点
DIAL_SETTLE = 2.5                  # 拖动后等待界面稳定
MAX_DIAL_DRAGS = 8                 # 每个方向最多拖几次(主线区域较多)
MAX_DIAL_SCANS = 10                # 探测进度时最多扫几档旋盘
MAX_LIST_SWIPES = 8               # 关卡列表最多滑动次数(单章最多 18 关)
SWIPE_MS = 800                    # 列表滑动时长(毫秒)
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
        """探测最新主线进度

        思路(用户给的, 已实测): 旋盘朝"最新"方向拖到底(=最新主线区域), 最新章节节点
        旁边的「x/y」进度文本就是进度; 当前横向位置看不到时再把地图横向拖到最右。
        方向实测: 向**上**拖到底才是最新区域(向下拖到底是最旧的狄斯西区 01-08)。
        """
        if not NAV_READY:
            return ""
        if not self._open_map(clicker):
            return ""
        self._drag_dial_to_end(clicker, direction="up")
        for _ in range(3):
            pair = self._find_progress_pair(clicker)
            if pair:
                logger.info(f"材料刷取: 地图进度 {pair}")
                return pair
            self._drag_map_to_end(clicker)
        logger.warning("材料刷取: 拖到底仍未找到主线进度文本")
        return ""

    def _drag_dial_to_end(self, clicker, direction="up", max_steps=8) -> None:
        """朝一个方向反复拖旋盘, 直到界面不再变化(到底)"""
        last = None
        for _ in range(max_steps):
            snapshot = tuple(sorted(self._screen_texts(clicker)))
            if snapshot == last:
                break
            last = snapshot
            self._dial_once(clicker, direction)

    def _drag_map_to_end(self, clicker, max_steps=6) -> None:
        """把地图横向拖到最右: 以当前可见章节节点的 y 为高度, 每次拖一屏"""
        anchor = None
        for text, _score, box in self._screen_items(clicker):
            if re.match(STAGE_CODE_RE, text.replace(" ", "")) or re.match(
                r"^[A-Za-z]{0,4}N?\d+$", text.replace(" ", "")
            ):
                anchor = box
                break
        y = (anchor[1] + anchor[3] / 2) / cfg.height if anchor else 0.40
        last = None
        for _ in range(max_steps):
            snapshot = tuple(sorted(self._screen_texts(clicker)))
            if snapshot == last:
                break
            last = snapshot
            clicker.swape([0.25, y, 8, 8], [0.85, y, 8, 8], SWIPE_MS)
            stop_sleep(1.5)

    def _find_progress_pair(self, clicker) -> str:
        """在地图区域(y>0.2)里找「章节文本 + x/y 进度」这一对, 返回如 N7-1/6"""
        items = self._screen_items(clicker)
        fractions = [
            (text.replace(" ", ""), box)
            for text, _score, box in items
            if re.match(r"^\d+/\d+$", text.replace(" ", ""))
            and (box[1] + box[3] / 2) / cfg.height > 0.2      # 排除右上角资源计数
        ]
        for frac_text, frac_box in fractions:
            best, best_x = None, -1
            for text, _score, box in items:
                token = text.replace(" ", "")
                if (
                    re.match(r"^N?\d+$", token)
                    and box[0] < frac_box[0]
                    and abs(box[1] - frac_box[1]) < 40
                    and box[0] > best_x
                ):
                    best, best_x = token, box[0]
            if best:
                return f"{best}-{frac_text}"
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
        """回到副本界面; 返回是否确认在副本界面上

        每轮: 已在副本界面 -> 返回; 有遮挡面板 -> 退掉;
        否则按 OCR 定位: 点「危机管理」标签确保停在卡片视图, 再点那张主线进度卡
        (卡上是"主线位置 + 关卡编号", 用编号正则/地区名定位)。
        """
        clicker.check_return_home()
        for _ in range(4):
            texts = self._screen_texts(clicker)
            if any(marker in texts for marker in MAP_MARKERS):
                if self._click_text(clicker, DIST_CITY):   # 确保在主线(狄斯城)标签
                    stop_sleep(1.0)
                return True
            if any(marker in texts for marker in OVERLAY_MARKERS):
                logger.info("材料刷取: 关闭遮挡面板")
                clicker.back()
                stop_sleep(1.2)
                continue
            # 1) 确保停在危机管理卡片视图
            self._click_text(clicker, CRISIS_MANAGE_TEXT)
            stop_sleep(1.5)
            # 2) 点进度卡: 优先用卡上的关卡编号(如 ReN7-2), 退而用地区名
            if not self._click_regex(clicker, STAGE_CODE_RE, times=1):
                self._click_text(clicker, CARD_FALLBACK_TEXT)
            stop_sleep(2.5)
        logger.warning(
            "材料刷取: 未能进入副本界面; 当前屏幕: "
            + " | ".join(self._screen_texts(clicker)[:15])
        )
        return False

    def _dial_once(self, clicker, direction="down") -> None:
        """按住左侧主线位置标签拖动一档

        关键(真机验证): 必须从"主线位置标签"上按住拖, 且带一点 x 漂移,
        纯竖直滑动游戏不认; duration 用毫秒。
        """
        best = None
        for text, _score, box in self._screen_items(clicker):
            if text.replace(" ", "") in REGION_LABELS:
                cx = (box[0] + box[2] / 2) / cfg.width
                cy = (box[1] + box[3] / 2) / cfg.height
                if best is None or abs(cy - 0.5) < abs(best[2] - 0.5):
                    best = (text, cx, cy)
        if best is None:
            _text, x, y = "兜底位置", *DIAL_FALLBACK
        else:
            _text, x, y = best
        travel = self._dial_travel(clicker)
        drift = DIAL_DRIFT_DOWN if direction == "down" else DIAL_DRIFT_UP
        end_y = y + travel if direction == "down" else y - travel
        clicker.swape([x, y, 8, 8], [x + drift, end_y, 8, 8], DIAL_MS)
        stop_sleep(DIAL_SETTLE)

    def _dial_travel(self, clicker) -> float:
        """拖动行程: 由 OCR 量出的「主线位置标签行距」推算

        实测行程 >=0.16 会被游戏忽略(拉过头), 因此取行距的 0.8 倍并限制在 0.06~0.12。
        """
        ys = sorted(
            (box[1] + box[3] / 2) / cfg.height
            for text, _s, box in self._screen_items(clicker)
            if text.replace(" ", "") in REGION_LABELS
        )
        gaps = [ys[i + 1] - ys[i] for i in range(len(ys) - 1)]
        if not gaps:
            return DIAL_TRAVEL_FALLBACK
        gap = sorted(gaps)[len(gaps) // 2]
        return max(DIAL_TRAVEL_MIN, min(gap * DIAL_TRAVEL_RATIO, DIAL_TRAVEL_MAX))

    def _goto_chapter(self, clicker, chapter) -> bool:
        """在地图上把目标章节滚到可见并点开(闭环: 每次拖动后重新观察)

        方向先按"可见章节号 vs 目标章节号"猜一次, 猜的方向拖满后换另一个方向,
        因此即使主线位置标签重名、顺序不确定也能收敛。
        """
        if self._click_text(clicker, chapter):
            return True
        target = int(re.sub(r"\D", "", chapter) or 0)
        visible = [
            int(text) for text in self._screen_texts(clicker) if re.match(r"^\d+$", text)
        ]
        first = "up" if target > max(visible or [0]) else "down"
        second = "down" if first == "up" else "up"
        for direction in (first, second):
            for _ in range(MAX_DIAL_DRAGS):
                logger.info(
                    f"材料刷取: 未见章节 {chapter}(可见 {sorted(visible)}), "
                    f"拖旋盘向{'上' if direction == 'up' else '下'}"
                )
                self._dial_once(clicker, direction)
                if self._click_text(clicker, chapter):
                    return True
                visible = [
                    int(text)
                    for text in self._screen_texts(clicker)
                    if re.match(r"^\d+$", text)
                ]
        logger.warning(
            f"材料刷取: 地图上未能找到章节 {chapter}; 当前屏幕: "
            + " | ".join(self._screen_texts(clicker)[:15])
        )
        return False

    def _click_regex(self, clicker, pattern, times=2) -> bool:
        """点击屏幕上匹配正则的第一个文本块(用于"结构稳定但内容变化"的文本)"""
        for _ in range(times):
            for text, _score, box in self._screen_items(clicker):
                cleaned = text.replace(" ", "")
                if re.match(pattern, cleaned):
                    x = (box[0] + box[2] / 2) / cfg.width
                    y = (box[1] + box[3] / 2) / cfg.height
                    logger.debug(f"材料刷取: 点击 {cleaned} @ ({x:.3f},{y:.3f})")
                    clicker.click_rate(x, y)
                    return True
            stop_sleep(0.6)
        logger.warning(f"材料刷取: 屏幕上没有匹配 {pattern} 的文本")
        return False

    def _enter_chapter(self, clicker, chapter) -> bool:
        """点章节节点 -> 详情面板 -> 再点标题区的进度文本进入关卡列表

        真机验证: 面板里的章节标题常被 OCR 读成 N/1/6(章号丢失), 但进度文本
        「数字/数字」稳定可读, 点它即可进入(等价于"再点一次章节名")。
        """
        if not self._click_text(clicker, chapter):
            return False
        stop_sleep(1.5)
        return self._click_regex(clicker, r"^\d+/\d+$")

    def _select_stage(self, clicker, stage) -> bool:
        """在章节关卡列表里选中目标关卡(游戏内编号与 wiki 一致, 如 N7-1)

        列表不可见时横向滑动: 滑动高度取当前可见关卡节点的 y(OCR 得到, 不写死)。
        """
        for _ in range(MAX_LIST_SWIPES + 1):
            if self._click_text(clicker, stage["code"]):
                return True
            row_y = None
            for text, _score, box in self._screen_items(clicker):
                code = text.replace(" ", "")
                if re.match(r"^[A-Za-z]*N?\d+-\d+$", code):
                    row_y = (box[1] + box[3] / 2) / cfg.height
                    break
            y = row_y if row_y else 0.59
            clicker.swape([0.85, y, 8, 8], [0.30, y, 8, 8], SWIPE_MS)
            stop_sleep(1.2)
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
        if not self._enter_chapter(clicker, stage["chapter"]):
            clicker.return_home()
            return "unavailable"
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
        clicker.click_rate(0.5, 0.1)                # 升级弹窗(点空白关闭)
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
