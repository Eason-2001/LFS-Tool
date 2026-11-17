# apps/converter/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# 导入我们之前写的转换引擎注册表
from converter_engine.engines import registry
import os
import uuid
from django.conf import settings
from rest_framework.parsers import MultiPartParser  # 处理文件上传必须的工具
from .serializers import FileConvertSerializer


class SupportedFormatView(APIView):
    """
    GET 接口：返回网站当前支持的所有文件转换格式
    前端打开页面的时候，拉这个接口，自动渲染下拉选项
    """
    def get(self, request):
        # 拿到注册表里所有的 (源格式, 目标格式) 列表
        supported_list = registry.supported()
        # 格式化成前端好读的结构
        data = [
            {
                "source": src,
                "target": dst,
                "label": f"{src.upper()} 转 {dst.upper()}"
            }
            for src, dst in supported_list
        ]
        return Response({
            "code": 200,
            "message": "success",
            "data": data
        }, status=status.HTTP_200_OK)

class FileConvertView(APIView):
    """
    POST接口：接收上传文件，执行格式转换，返回下载链接
    """
    # 声明这个接口要处理文件上传（普通JSON接口不需要这个）
    parser_classes = [MultiPartParser]
    serializer_class = FileConvertSerializer

    def post(self, request):
        # 1. 从请求里拿前端传过来的两个东西：上传的文件、目标格式
        upload_file = request.FILES.get("file")
        target_format = request.data.get("target_format")

        # 先做基础校验，缺东西直接返回错误
        if not upload_file:
            return Response({"code": 400, "message": "请上传文件"}, status=status.HTTP_400_BAD_REQUEST)
        if not target_format:
            return Response({"code": 400, "message": "请选择目标格式"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. 从文件名里拆出来源格式（后缀）
        original_filename = upload_file.name
        # 把文件名按最后一个点切开，后面那部分就是后缀，转小写
        source_format = original_filename.split(".")[-1].lower()

        # 3. 找注册表里对应的转换器
        converter_cls = registry.find(source_format, target_format)
        if not converter_cls:
            return Response(
                {"code": 400, "message": f"暂不支持 {source_format} 转 {target_format}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4. 生成唯一文件名，避免两个用户传同名文件互相覆盖
        # 用uuid生成一个随机ID，谁也不会撞名
        unique_id = uuid.uuid4().hex
        # 临时输入文件路径：存在tmp_uploads里
        temp_input_path = os.path.join("tmp_uploads", f"{unique_id}_{original_filename}")
        # 输出文件路径：存在outputs里，文件名就是随机ID+目标后缀
        output_filename = f"{unique_id}.{target_format}"
        output_path = os.path.join("outputs", output_filename)

        # 把用户上传的临时文件，真正写到磁盘上
        with open(temp_input_path, "wb") as f:
            for chunk in upload_file.chunks():
                f.write(chunk)

        # 5. 调用转换器干活
        converter = converter_cls()  # 注意：find拿回来的是类，要先实例化！
        converter.convert(temp_input_path, output_path)

        # 6. 把下载链接拼好，返回给前端
        download_url = f"/media/{output_filename}"
        return Response({
            "code": 200,
            "message": "转换成功",
            "data": {
                "download_url": download_url,
                "original_name": original_filename
            }
        }, status=status.HTTP_200_OK)
