# apps/accounts/serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Memo


class RegisterSerializer(serializers.Serializer):
    """注册：校验用户名唯一、两次密码一致，创建用户（密码由 Django 哈希存储）"""

    username = serializers.CharField(min_length=3, max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户名已被注册")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "两次输入的密码不一致"})
        return attrs

    def create(self, validated_data):
        # create_user 会自动对密码做哈希，不能用 objects.create 存明文
        return User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )


class UserSerializer(serializers.ModelSerializer):
    """对外返回的用户信息，不包含密码等敏感字段"""

    class Meta:
        model = User
        fields = ["id", "username"]


class MemoSerializer(serializers.ModelSerializer):
    """备忘录序列化：时间字段只读，由后端自动维护"""

    class Meta:
        model = Memo
        fields = ["id", "title", "content", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]
