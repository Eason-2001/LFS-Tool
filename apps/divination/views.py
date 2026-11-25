import calendar

from django.utils.timezone import localdate
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .models import DivinationRecord
from .serializers import HistorySerializer


def _bad_request(message):
    return Response({"code": 400, "message": message, "data": None}, status=status.HTTP_400_BAD_REQUEST)


def _gate_int(value, lo, hi, name):
    try:
        v = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name}须为整数")
    if not (lo <= v <= hi):
        raise ValueError(f"{name}超出有效范围")
    return v


class BaziView(APIView):
    """POST /api/divination/bazi/  中式命理：紫微排盘 + 生肖运势 + 当日黄历"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        try:
            year = _gate_int(data.get("year"), 1901, 2099, "出生年")
            month = _gate_int(data.get("month"), 1, 12, "出生月")
            day = _gate_int(data.get("day"), 1, 31, "出生日")
            hour = _gate_int(data.get("hour"), 0, 23, "出生时")
            minute = _gate_int(data.get("minute"), 0, 59, "出生分")
        except ValueError as exc:
            return _bad_request(str(exc))

        gender = str(data.get("gender", "")).lower()
        if gender not in ("m", "f"):
            return _bad_request("性别须为 m（男）或 f（女）")

        max_day = calendar.monthrange(year, month)[1]
        if day > max_day:
            return _bad_request(f"{month} 月没有 {day} 日，请核对日期")

        birth_time = f"{year}-{month:02d}-{day:02d} {hour:02d}"

        # 第一段：紫微斗数排盘（必须成功，是整套中式结果的基础）
        pan, err = services.fetch_ziwei(birth_time, gender)
        if err:
            return Response({"code": 502, "message": err, "data": None}, status=status.HTTP_502_BAD_GATEWAY)

        warnings = []

        # 第二段：生肖今日 / 本月运势（可降级，失败不阻断主流程）
        fortune = None
        sx_py = services._sx_to_pinyin(pan.get("sx"))
        if sx_py:
            fortune, ferr = services.fetch_zodiac_fortune(sx_py)
            if ferr:
                warnings.append(f"生肖运势暂不可用：{ferr}")
        else:
            warnings.append("未能从命盘解析生肖，跳过生肖运势")

        # 第三段：当日黄历宜忌（可降级）
        today = localdate()
        huangli, herr = services.fetch_huangli(today.strftime("%Y%m%d"))
        if herr:
            warnings.append(f"今日黄历暂不可用：{herr}")

        result = {"pan": pan, "fortune": fortune, "huangli": huangli, "warnings": warnings}
        summary = f"{pan.get('sx') or ''} · 命主{pan.get('mz') or '—'}"

        DivinationRecord.objects.create(
            user=request.user,
            kind=DivinationRecord.KIND_BAZI,
            input={"birth_time": birth_time, "gender": gender},
            result=result,
            summary=summary,
        )

        return Response({"code": 200, "message": "success", "data": result})


class HoroscopeView(APIView):
    """POST /api/divination/horoscope/  西式星座：按阳历生日判星座，取本月运势"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        try:
            month = _gate_int(data.get("month"), 1, 12, "出生月")
            day = _gate_int(data.get("day"), 1, 31, "出生日")
        except ValueError as exc:
            return _bad_request(str(exc))

        sign_en, sign_cn = services.judge_zodiac(month, day)

        horo, err = services.fetch_monthly_horoscope(sign_en)
        if err:
            return Response({"code": 502, "message": err, "data": None}, status=status.HTTP_502_BAD_GATEWAY)

        result = {"sign_cn": sign_cn, "sign_en": sign_en, **horo}
        summary = f"{sign_cn} · 本月运势"

        DivinationRecord.objects.create(
            user=request.user,
            kind=DivinationRecord.KIND_HOROSCOPE,
            input={"month": month, "day": day},
            result=result,
            summary=summary,
        )

        return Response({"code": 200, "message": "success", "data": result})


class TarotView(APIView):
    """POST /api/divination/tarot/  命运塔罗：按牌阵抽牌并解读"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        spread = str(request.data.get("spread", "daily")).lower()
        if spread not in services.TAROT_SPREADS:
            return _bad_request("牌阵须为 daily / three / love")

        question = str(request.data.get("question", "")).strip()[:100]
        if not question:
            return _bad_request("请先写下你想问的问题")
        cfg = services.TAROT_SPREADS[spread]
        cards = services.draw_tarot(spread)

        # 大模型结合提问做个性化解读；未配置 Key / 调用失败时返回 None，逐牌回退静态牌意
        ai = services.analyze_tarot(cards, question, cfg["label"])
        ai_cards = ai["cards"] if ai else []
        for idx, card in enumerate(cards):
            card["ai_reading"] = ai_cards[idx] if idx < len(ai_cards) else None
        ai_summary = ai["summary"] if ai else ""

        result = {"spread": spread, "cards": cards, "summary": ai_summary}
        summary = f"{cfg['label']} · {cards[0]['name']}"

        DivinationRecord.objects.create(
            user=request.user,
            kind=DivinationRecord.KIND_TAROT,
            input={"spread": spread, "question": question},
            result=result,
            summary=summary,
        )

        return Response({"code": 200, "message": "success", "data": result})


class TarotCardView(APIView):
    """GET /api/divination/tarot/card/?id=&direction=  单张塔罗牌详情（只读，不落库）"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            card_id = _gate_int(request.GET.get("id"), 0, 77, "牌 id")
        except ValueError as exc:
            return _bad_request(str(exc))

        direction = str(request.GET.get("direction", "upright")).lower()
        upright = direction != "reversed"

        card = services.get_tarot_card(card_id, upright)
        if not card:
            return _bad_request("未找到该塔罗牌")

        return Response({"code": 200, "message": "success", "data": card})


class HistoryView(APIView):
    """GET /api/divination/history/  当前用户最近的测算记录"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = DivinationRecord.objects.filter(user=request.user)[:20]
        data = HistorySerializer(qs, many=True).data
        return Response({"code": 200, "message": "success", "data": data})
