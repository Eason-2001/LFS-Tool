from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import GameRecord
from .serializers import LeaderboardSerializer

# 各游戏成绩方向：higher 分数越高越好；lower 用时越短越好
# 扫雷按难度分榜，避免不同雷量混排不公平
GAMES = {
    "breakout": "higher",
    "tetris": "higher",
    "spider": "lower",
    "minesweeper-easy": "lower",
    "minesweeper-medium": "lower",
    "minesweeper-hard": "lower",
}
TOP_N = 10


def _is_lower(game):
    return GAMES[game] == "lower"


class ScoreSubmitView(APIView):
    """POST /api/game/score/ 上报一局成绩：更新历史最佳与局数，返回当前最佳和名次"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        game = request.data.get("game", "breakout")
        if game not in GAMES:
            return Response(
                {"code": 400, "message": "游戏标识无效"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        score = request.data.get("score")
        if not isinstance(score, int) or score < 0:
            return Response(
                {"code": 400, "message": "成绩无效"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        record, created = GameRecord.objects.get_or_create(
            user=request.user,
            game=game,
            defaults={"best_score": score, "plays": 1},
        )
        if not created:
            record.plays += 1
            if _is_lower(game):
                # 用时越短越好：best_score 为 0 视为尚无成绩
                if record.best_score == 0 or score < record.best_score:
                    record.best_score = score
            elif score > record.best_score:
                record.best_score = score
            record.save()

        # 名次：比自己更优的人数 + 1（同分并列）
        qs = GameRecord.objects.filter(game=game)
        if _is_lower(game):
            rank = qs.filter(best_score__gt=0, best_score__lt=record.best_score).count() + 1
        else:
            rank = qs.filter(best_score__gt=record.best_score).count() + 1

        return Response(
            {
                "code": 200,
                "message": "success",
                "data": {"best": record.best_score, "plays": record.plays, "rank": rank},
            }
        )


class LeaderboardView(APIView):
    """GET /api/game/leaderboard/?game=xxx 排行榜 Top N，外加当前玩家自己的名次"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        game = request.query_params.get("game", "breakout")
        if game not in GAMES:
            return Response(
                {"code": 400, "message": "游戏标识无效"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = GameRecord.objects.filter(game=game).select_related("user")

        if _is_lower(game):
            # 用时少优先：排除尚无成绩（0 秒）的记录
            ordered = qs.exclude(best_score=0).order_by("best_score", "updated_at")
        else:
            ordered = qs.order_by("-best_score", "-updated_at")
        top = ordered[:TOP_N]
        top_data = LeaderboardSerializer(top, many=True).data

        me = qs.filter(user=request.user).first()
        me_data = None
        if me:
            if _is_lower(game):
                rank = qs.filter(best_score__gt=0, best_score__lt=me.best_score).count() + 1
            else:
                rank = qs.filter(best_score__gt=me.best_score).count() + 1
            me_data = {"rank": rank, "best": me.best_score, "plays": me.plays}

        return Response(
            {
                "code": 200,
                "message": "success",
                "data": {"top": top_data, "me": me_data},
            }
        )
