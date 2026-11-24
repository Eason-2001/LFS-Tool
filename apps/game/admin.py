from django.contrib import admin

from .models import GameRecord


@admin.register(GameRecord)
class GameRecordAdmin(admin.ModelAdmin):
    list_display = ("user", "game", "best_score", "plays", "updated_at")
    list_filter = ("game",)
    search_fields = ("user__username",)
