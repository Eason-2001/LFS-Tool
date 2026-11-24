from django.db import models
from django.contrib.auth.models import User


class GameRecord(models.Model):
    """玩家在某款游戏上的成绩档案：每用户每游戏唯一一条，存历史最佳与对局次数"""

    GAME_BREAKOUT = "breakout"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="game_records",
        verbose_name="玩家",
    )
    game = models.CharField("游戏标识", max_length=32, default=GAME_BREAKOUT)
    best_score = models.IntegerField("历史最佳", default=0)
    plays = models.IntegerField("对局次数", default=0)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        # 同一玩家同一游戏只留一条档案
        unique_together = ("user", "game")
        ordering = ["-best_score", "-updated_at"]

    def __str__(self):
        return f"{self.user.username} · {self.game} · {self.best_score}"
