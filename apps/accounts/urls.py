# apps/accounts/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView,
    MemoDetailView,
    MemoImageUploadView,
    MemoListView,
    RegisterView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    # access 过期后，用 refresh 令牌换新 access（simplejwt 内置视图）
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # 备忘录插图上传（字符串路由，放在 <int:pk> 前避免歧义）
    path("memos/upload-image/", MemoImageUploadView.as_view(), name="memo-upload-image"),
    # 备忘录：列表/新建 与 单条改/删
    path("memos/", MemoListView.as_view(), name="memo-list"),
    path("memos/<int:pk>/", MemoDetailView.as_view(), name="memo-detail"),
]
