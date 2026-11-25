# 第三方命理 / 星座接口封装
# 所有 appKey 只留在后端环境变量，前端不直接接触第三方服务
import random

import requests
from django.conf import settings

from . import tarot_data

HTTP_TIMEOUT = 12

SHOWAPI_BASE = "https://route.showapi.com"
FREE_HORO_BASE = "https://freehoroscopeapi.com/api/v1/get-horoscope"

# 中文生肖 → ShowAPI 生肖拼音码（2219 入参）
SX_PINYIN = {
    "鼠": "shu", "牛": "niu", "虎": "hu", "兔": "tu", "龙": "long",
    "蛇": "she", "马": "ma", "羊": "yang", "猴": "hou", "鸡": "ji",
    "狗": "gou", "猪": "zhu",
}

# 12 星座：起止月日、英文 sign、中文名。摩羯座跨年末年初，单独放最后兜底
ZODIAC_RANGES = [
    ((1, 20), (2, 18), "aquarius", "水瓶座"),
    ((2, 19), (3, 20), "pisces", "双鱼座"),
    ((3, 21), (4, 19), "aries", "白羊座"),
    ((4, 20), (5, 20), "taurus", "金牛座"),
    ((5, 21), (6, 21), "gemini", "双子座"),
    ((6, 22), (7, 22), "cancer", "巨蟹座"),
    ((7, 23), (8, 22), "leo", "狮子座"),
    ((8, 23), (9, 22), "virgo", "处女座"),
    ((9, 23), (10, 23), "libra", "天秤座"),
    ((10, 24), (11, 22), "scorpio", "天蝎座"),
    ((11, 23), (12, 21), "sagittarius", "射手座"),
]


def judge_zodiac(month, day):
    """按阳历月日判定星座，返回 (英文 sign, 中文名)；越界返回 None"""
    day = int(day)
    for (m1, d1), (m2, d2), en, cn in ZODIAC_RANGES:
        if month == m1 and day >= d1:
            return en, cn
        if month == m2 and day <= d2:
            return en, cn
    # 12/22 ~ 1/19 摩羯
    return "capricorn", "摩羯座"


def _showapi_get(code_point, params):
    """请求 ShowAPI 接入点，返回 (body, 错误信息)；成功时错误信息为 None"""
    key = settings.SHOWAPI_KEY
    if not key:
        return None, "命理服务未配置（缺少 SHOWAPI_KEY）"

    try:
        resp = requests.get(
            f"{SHOWAPI_BASE}/{code_point}",
            params={"appKey": key, **params},
            timeout=HTTP_TIMEOUT,
        )
        resp.raise_for_status()
        payload = resp.json()
    except requests.RequestException as exc:
        return None, f"命理请求失败: {exc}"

    body = payload.get("showapi_res_body") or {}
    if str(body.get("ret_code")) != "0":
        return None, body.get("remark") or "命理接口返回失败"
    return body, None


def _sx_to_pinyin(sx_text):
    """从生肖中文文本（如『属羊』『羊』）里匹配拼音码；上游若已返回拼音码则直接放行"""
    if not sx_text:
        return None
    for cn, py in SX_PINYIN.items():
        if cn in sx_text:
            return py
    if sx_text in SX_PINYIN.values():
        return sx_text
    return None


def fetch_ziwei(birth_time, gender):
    """1647 紫微斗数排盘：birth_time=yyyy-MM-dd HH，gender=m/f"""
    body, err = _showapi_get("1647-1", {"time": birth_time, "gender": gender})
    if err:
        return None, err
    result = body.get("result") or {}
    pan_list = result.get("pan") or []
    # 顶层不返回干支，命宫干支与主星从十二宫里取命宫宫位
    ming = next((p for p in pan_list if p.get("palace") == "命宫"), {})
    pan = {
        "wx": result.get("wx"),          # 五行局
        "mg": result.get("mg"),          # 命宫
        "mz": result.get("mz"),          # 命主
        "sz": result.get("sz"),          # 身主
        "sg": result.get("sg"),          # 身宫
        "yy": result.get("yy"),          # 阴阳
        "sx": result.get("sx"),          # 生肖（中文）
        "branch": ming.get("branch"),    # 命宫干支
        "ming_main": "、".join(ming.get("main") or []),  # 命宫主星
    }
    return pan, None


def fetch_zodiac_fortune(sx_pinyin, need_month=True):
    """2219 生肖运势：今日 +（可选）本月"""
    params = {"sx": sx_pinyin}
    if need_month:
        params["needMonth"] = "1"
    body, err = _showapi_get("2219-1", params)
    if err:
        return None, err
    return {
        "shenxiao": body.get("shenxiao"),
        "day": body.get("day"),
        "month": body.get("month"),
    }, None


def fetch_huangli(ymd):
    """856-2 当日黄历宜忌：ymd=yyyyMMdd"""
    body, err = _showapi_get("856-2", {"ymd": ymd})
    if err:
        return None, err
    return {
        "nongli": body.get("nongli"),
        "ganzhi": body.get("ganzhi"),
        "zhishen": body.get("zhishen"),
        "yi": body.get("yi"),
        "ji": body.get("ji"),
        "chongsha": body.get("chongsha"),
        "nayin": body.get("nayin"),
    }, None


def translate_to_zh(text):
    """32-10 英译中：返回 (译文, 错误信息)；失败时译文为 None"""
    if not text:
        return text, None
    body, err = _showapi_get("32-10", {"q": text, "from": "en", "to": "zh"})
    if err:
        return None, err
    tr = body.get("translation") or []
    if not tr:
        return None, "翻译结果为空"
    return tr[0], None


def fetch_monthly_horoscope(sign_en):
    """freehoroscopeapi 免 key 月度星座运势，英文原文经 32-10 译为中文；翻译失败降级保留英文"""
    try:
        resp = requests.get(
            f"{FREE_HORO_BASE}/monthly",
            params={"sign": sign_en},
            timeout=HTTP_TIMEOUT,
        )
        resp.raise_for_status()
        payload = resp.json()
    except requests.RequestException as exc:
        return None, f"星座运势请求失败: {exc}"

    data = payload.get("data") or {}
    en_text = data.get("horoscope")
    if not en_text:
        return None, "未获取到本月运势"

    zh_text, terr = translate_to_zh(en_text)
    return {
        "date": data.get("date"),
        "period": "本月",
        "sign": data.get("sign"),
        "horoscope": zh_text or en_text,
        "horoscope_en": en_text,
        "translate_failed": bool(terr),
    }, None


# ---------- 塔罗牌（本地牌库，无第三方依赖） ----------

# 牌阵：daily 每日一牌 / three 三牌占卜 / love 爱情占卜
TAROT_SPREADS = {
    "daily": {"count": 1, "positions": ["今日指引"], "label": "每日一牌"},
    "three": {"count": 3, "positions": ["过去", "现在", "未来"], "label": "三牌占卜"},
    "love": {"count": 3, "positions": ["你的期待", "关系现状", "未来走向"], "label": "爱情占卜"},
}


def draw_tarot(spread):
    """按牌阵从不重复的牌堆中随机抽牌，并随机决定正位 / 逆位，返回结构化牌阵"""
    cfg = TAROT_SPREADS[spread]
    picked = random.sample(tarot_data.TAROT_DECK, cfg["count"])
    cards = []
    for position, card in zip(cfg["positions"], picked):
        upright = random.random() < 0.5
        cards.append(
            {
                "position": position,
                "id": card["id"],
                "name": card["name"],
                "name_en": card["name_en"],
                "suit": card.get("suit", "major"),
                "upright": upright,
                "keywords": card["keywords_up"] if upright else card["keywords_down"],
                "reading": card["up"] if upright else card["down"],
            }
        )
    return cards
