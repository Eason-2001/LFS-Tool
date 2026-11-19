#!/usr/bin/env python3
# coding=utf-8
# @Time    :2026/11/12 16:17
# @Author  :liufushuang
# 所有转换器在这里"登记"——以后加新格式，只加一行 import + register
from .registry import registry
# 导入转换器文件，触发装饰器自动注册
from . import markdown_html
from . import image_converter
from . import doc_text_converter
from . import docx_pdf_converter
