#!/usr/bin/env python3
# coding=utf-8
# @Time    :2026/11/12 16:17
# @Author  :liufushuang

class ConverterRegistry:
    """转换器注册表：登记、查找。"""
    def __init__(self):
        self._converter_map = {}

    def register(self, cls):
        # cls 是转换器类，不是实例
        for src, dst in cls.supports():
            self._converter_map[(src, dst)] = cls
        return cls

    def find(self, source_format, target_format):
        return self._converter_map.get((source_format, target_format))

    def supported(self):
        return list(self._converter_map.keys())

# 全局实例 + 装饰器别名
registry = ConverterRegistry()
register_converter = registry.register
