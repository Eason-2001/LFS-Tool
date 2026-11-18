#!/usr/bin/env python3
# coding=utf-8
# @Time    :2026/11/12 16:17
# @Author  :liufushuang
import markdown
from .base import BaseConverter
from .registry import register_converter


@register_converter
class MarkdownToHtmlConverter(BaseConverter):
    # 标记属于文档类
    category = "document"
    category_name = "文档格式转换"
    @staticmethod
    def supports():
        # 声明支持哪些转换配对，会自动注册进注册表
        return [
            ("md", "html")
        ]

    def convert(self, input_path: str, output_path: str):
        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()
        html = markdown.markdown(text)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
