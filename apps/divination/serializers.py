from rest_framework import serializers

from .models import DivinationRecord


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DivinationRecord
        fields = ["id", "kind", "input", "result", "summary", "created_at"]
