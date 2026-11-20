# apps/accounts/views.py
import os
import uuid

from django.contrib.auth import authenticate
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Memo
from .serializers import MemoSerializer, RegisterSerializer, UserSerializer

# 备忘录插图允许的类型与大小上限
ALLOWED_IMAGE_EXT = {"jpg", "jpeg", "png", "gif", "webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024


def _tokens_for_user(user):
    """为指定用户生成 JWT 双令牌：access 访问用，refresh 换新 access"""
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


class RegisterView(APIView):
    """POST /api/accounts/register/  注册新用户"""

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "code": 200,
                "message": "注册成功",
                "data": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """POST /api/accounts/login/  校验账号密码，成功后返回用户信息 + 双令牌"""

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"code": 400, "message": "请输入用户名和密码"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # authenticate 校验用户名密码，成功返回用户对象，失败返回 None
        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {"code": 400, "message": "用户名或密码错误"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = UserSerializer(user).data
        data.update(_tokens_for_user(user))
        return Response(
            {"code": 200, "message": "success", "data": data},
            status=status.HTTP_200_OK,
        )


class MemoListView(APIView):
    """备忘录列表：GET 查当前用户全部；POST 新建一条"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        memos = request.user.memos.all()
        return Response(
            {"code": 200, "message": "success", "data": MemoSerializer(memos, many=True).data}
        )

    def post(self, request):
        serializer = MemoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 归属人强制设为当前登录用户，前端传什么都改不了
        serializer.save(user=request.user)
        return Response(
            {"code": 200, "message": "创建成功", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )


class MemoDetailView(APIView):
    """单条备忘录：GET 查看 / PUT 修改 / DELETE 删除，只能操作自己的"""

    permission_classes = [IsAuthenticated]

    def _get_memo(self, request, pk):
        # 同时按主键和当前用户过滤，查不到别人的或不存在的都返回 404
        return get_object_or_404(Memo, pk=pk, user=request.user)

    def get(self, request, pk):
        memo = self._get_memo(request, pk)
        return Response(
            {"code": 200, "message": "success", "data": MemoSerializer(memo).data}
        )

    def put(self, request, pk):
        memo = self._get_memo(request, pk)
        serializer = MemoSerializer(memo, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"code": 200, "message": "更新成功", "data": serializer.data})

    def delete(self, request, pk):
        memo = self._get_memo(request, pk)
        memo.delete()
        return Response({"code": 200, "message": "删除成功"})


class MemoImageUploadView(APIView):
    """POST /api/accounts/memos/upload-image/  上传备忘录插图，返回可访问 URL"""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        image = request.FILES.get("image")
        if not image:
            return Response(
                {"code": 400, "message": "未收到图片"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ext = image.name.split(".")[-1].lower()
        if ext not in ALLOWED_IMAGE_EXT:
            return Response(
                {"code": 400, "message": "仅支持 jpg/png/gif/webp 图片"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if image.size > MAX_IMAGE_SIZE:
            return Response(
                {"code": 400, "message": "图片不能超过 5MB"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 存到 outputs/memo_images/，文件名用 uuid 避免重名覆盖
        upload_dir = os.path.join(settings.MEDIA_ROOT, "memo_images")
        os.makedirs(upload_dir, exist_ok=True)
        filename = f"{uuid.uuid4().hex}.{ext}"
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, "wb") as f:
            for chunk in image.chunks():
                f.write(chunk)

        url = f"/media/memo_images/{filename}"
        return Response(
            {"code": 200, "message": "上传成功", "data": {"url": url}}
        )
