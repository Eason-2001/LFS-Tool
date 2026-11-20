# apps/accounts/models.py
from django.db import models
from django.contrib.auth.models import User


class LongTextField(models.TextField):
    """MySQL LONGTEXT：比默认 TEXT(64KB) 更大，存富文本 HTML + 图片地址够用"""

    def db_type(self, connection):
        return "longtext"


class Memo(models.Model):
    """备忘录：一条只属于一个用户"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="memos",  # 反向查询：user.memos 拿到该用户所有备忘录
        verbose_name="归属用户",
    )
    title = models.CharField("标题", max_length=200)
    content = LongTextField("正文(富文本HTML)", blank=True, default="")
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ["-updated_at"]  # 列表按最近更新排前面

    def __str__(self):
        return self.title
