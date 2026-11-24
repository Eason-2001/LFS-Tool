from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import GameRecord
from .serializers import LeaderboardSerializer

GAME = "breakout"
TOP_N = 10


class ScoreSubmitView(APIView):
    """POST /api/game/score/ 上报一局成绩：更新历史最佳与局数，返回当前最佳和名次"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        score = request.data.get("score")
        if not isinstance(score, int) or score < 0:
            return Response(
                {"code": 400, "message": "成绩无效"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        record, created = GameRecord.objects.get_or_create(
            user=request.user,
            game=GAME,
            defaults={"best_score": score, "plays": 1},
        )
        if not created:
            record.plays += 1
            if score > record.best_score:
                record.best_score = score
            record.save()

        # 名次：分数比自己高的人数 + 1（同分并列）
        qs = GameRecord.objects.filter(game=GAME)
        rank = qs.filter(best_score__gt=record.best_score).count() + 1

        return Response(
            {
                "code": 200,
                "message": "success",
                "data": {"best": record.best_score, "plays": record.plays, "rank": rank},
            }
        )


class LeaderboardView(APIView):
    """GET /api/game/leaderboard/ 排行榜 Top N，外加当前玩家自己的名次"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = GameRecord.objects.filter(game=GAME).select_related("user")
        top = qs.order_by("-best_score", "-updated_at")[:TOP_N]
        top_data = LeaderboardSerializer(top, many=True).data

        me = qs.filter(user=request.user).first()
        me_data = None
        if me:
            rank = qs.filter(best_score__gt=me.best_score).count() + 1
            me_data = {"rank": rank, "best": me.best_score, "plays": me.plays}

        return Response(
            {
                "code": 200,
                "message": "success",
                "data": {"top": top_data, "me": me_data},
            }
        )
