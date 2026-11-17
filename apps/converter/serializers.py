#!/usr/bin/env python3
# coding=utf-8
# @Time    :2026/11/17 16:02
# @Author  :liufushuang
from rest_framework import serializers


class FileConvertSerializer(serializers.Serializer):
    # 告诉DRF：这个接口要收两个参数
    # 一个是用户上传的文件
    file = serializers.FileField()
    # 一个是用户选的目标格式
    target_format = serializers.CharField()
