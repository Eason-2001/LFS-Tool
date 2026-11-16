#!/usr/bin/env python3
# coding=utf-8
# @Time    :2026/11/12 16:16
# @Author  :liufushuang
class BaseConverter:
    """所有转换器的基类：定义统一的转换接口。"""

    name = ""              # 显示名
    source_format = ""     # 源格式，如 "md"
    target_format = ""     # 目标格式，如 "html"

    def can_convert(self, source_format, target_format):
        """判断本转换器能否处理这对格式。"""
        return (
            source_format.lower() == self.source_format
            and target_format.lower() == self.target_format
        )

    def convert(self, input_path, output_path):
        """真正执行转换，子类必须实现。"""
        raise NotImplementedError("子类必须实现 convert() 方法")
