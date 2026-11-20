from django.contrib import admin

from .models import Memo


@admin.register(Memo)
class MemoAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "user", "updated_at", "created_at"]
    list_filter = ["user"]
    search_fields = ["title", "content"]
