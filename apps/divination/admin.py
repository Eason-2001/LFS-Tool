from django.contrib import admin

from .models import DivinationRecord


@admin.register(DivinationRecord)
class DivinationRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "kind", "summary", "created_at")
    list_filter = ("kind", "created_at")
    search_fields = ("user__username", "summary")
