#!/usr/bin/env python3
# coding=utf-8
# @Time    :2026/11/16 15:47
# @Author  :liufushuang

from .base import BaseConverter
from .registry import register_converter
from PIL import Image

@register_converter
class ImageConverter(BaseConverter):
    @staticmethod
    def supports():
        # 声明支持哪些转换配对，会自动注册进注册表
        return [
            ("png", "jpg"),
            ("jpg", "webp"),
            ("png", "webp")
        ]

    def convert(self, input_path: str, output_path: str):
        # 打开源文件
        with Image.open(input_path) as img:
            # 特殊处理：jpg不支持透明通道，png转jpg要垫白底
            if output_path.lower().endswith(".jpg") or output_path.lower().endswith(".jpeg"):
                # 新建白底画布
                rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                # 把原图贴上去，带上透明蒙版
                mask = img.split()[-1] if img.mode == "RGBA" else None
                rgb_img.paste(img, mask=mask)
                rgb_img.save(output_path, quality=85)
            else:
                # webp直接保存，支持透明
                img.save(output_path)
