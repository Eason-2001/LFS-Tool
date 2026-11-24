from django.db import models
from django.contrib.auth.models import User


class DivinationRecord(models.Model):
    """一次命理/星座测算记录：保存用户输入与第三方接口返回的结构化结果"""

    KIND_BAZI = "bazi"
    KIND_HOROSCOPE = "horoscope"
    KIND_CHOICES = [
        (KIND_BAZI, "中式命理"),
        (KIND_HOROSCOPE, "西式星座"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="divination_records",
        verbose_name="用户",
    )
    kind = models.CharField("测算类型", max_length=16, choices=KIND_CHOICES)
    input = models.JSONField("测算输入", default=dict)
    result = models.JSONField("测算结果", default=dict)
    summary = models.CharField("结果摘要", max_length=255, blank=True, default="")
    created_at = models.DateTimeField("测算时间", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} · {self.kind} · {self.created_at:%Y-%m-%d %H:%M}"
