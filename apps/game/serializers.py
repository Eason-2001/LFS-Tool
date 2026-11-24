from rest_framework import serializers

from apps.accounts.models import Profile
from .models import GameRecord


class LeaderboardSerializer(serializers.ModelSerializer):
    """排行榜条目：分数之外带出玩家昵称、头像（来自关联 Profile）"""

    username = serializers.CharField(source="user.username")
    nickname = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = GameRecord
        fields = ["username", "nickname", "avatar", "best_score", "plays"]

    @staticmethod
    def _profile(user):
        profile, _ = Profile.objects.get_or_create(user=user)
        return profile

    def get_nickname(self, record):
        return self._profile(record.user).nickname

    def get_avatar(self, record):
        avatar = self._profile(record.user).avatar
        return avatar.url if avatar else None
