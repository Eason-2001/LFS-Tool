# apps/life/views.py
# 生活信息：天气（心知天气代理）
# 第三方 Key 只放在后端，前端不直接接触，避免泄露
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

SENIVERSE_BASE = "https://api.seniverse.com/v3/weather"
HTTP_TIMEOUT = 5

# 浏览器定位失败 / 拒绝授权时兜底城市：成都（纬度:经度，心知坐标顺序）
DEFAULT_LOCATION = "30.57:104.06"


def _seniverse_get(path, location, extra=None):
    """请求心知天气，返回 (results[0], 错误信息)；成功时错误信息为 None"""
    key = settings.SENIVERSE_KEY
    if not key:
        return None, "天气服务未配置（缺少 SENIVERSE_KEY）"

    params = {
        "key": key,
        "location": location,
        "language": "zh-Hans",
        "unit": "c",
    }
    if extra:
        params.update(extra)

    try:
        resp = requests.get(f"{SENIVERSE_BASE}/{path}", params=params, timeout=HTTP_TIMEOUT)
        resp.raise_for_status()
        payload = resp.json()
    except requests.RequestException as exc:
        return None, f"天气请求失败: {exc}"

    results = payload.get("results") or []
    if not results:
        return None, payload.get("status", "未查到该位置的天气")
    return results[0], None


class WeatherView(APIView):
    """GET /api/life/weather/?lng=&lat=  天气实况 + 3 天预报（公开）"""

    def get(self, request):
        lng = request.query_params.get("lng")
        lat = request.query_params.get("lat")

        if lng and lat:
            try:
                # 心知坐标格式为「纬度:经度」，冒号分隔，顺序不能反
                location = f"{float(lat)}:{float(lng)}"
            except ValueError:
                location = DEFAULT_LOCATION
        else:
            location = DEFAULT_LOCATION

        now_res, err = _seniverse_get("now.json", location)
        if err:
            return Response(
                {"code": 502, "message": err, "data": None},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        daily_res, _ = _seniverse_get("daily.json", location, {"days": "3"})

        now = now_res.get("now", {})
        daily = []
        if daily_res:
            for item in daily_res.get("daily", []):
                daily.append(
                    {
                        "date": item.get("date"),
                        "text_day": item.get("text_day"),
                        "text_night": item.get("text_night"),
                        "code_day": item.get("code_day"),
                        "high": item.get("high"),
                        "low": item.get("low"),
                    }
                )

        data = {
            "city": now_res.get("location", {}).get("name"),
            "now": {
                "text": now.get("text"),
                "code": now.get("code"),
                "temperature": now.get("temperature"),
                "feels_like": now.get("feels_like"),
                "humidity": now.get("humidity"),
                "wind_direction": now.get("wind_direction"),
            },
            "daily": daily,
        }
        return Response({"code": 200, "message": "success", "data": data})
