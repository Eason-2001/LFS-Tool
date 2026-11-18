#!/usr/bin/env python3
# coding=utf-8
# @Time    :2026/11/12 16:17
# @Author  :liufushuang

class ConverterRegistry:
    def __init__(self):
        self._converter_map = {}
        # 存分类的中文名
        self._category_names = {}

    def register(self, cls):
        # 登记分类名
        self._category_names[cls.category] = cls.category_name
        for src, dst in cls.supports():
            self._converter_map[(src, dst)] = {
                "converter": cls,
                "category": cls.category
            }
        return cls

    def find(self, source_format, target_format):
        item = self._converter_map.get((source_format, target_format))
        return item["converter"] if item else None

    def grouped_supported(self):
        """按分类整理好返回给前端"""
        groups = {}
        for (src, dst), info in self._converter_map.items():
            cat = info["category"]
            if cat not in groups:
                groups[cat] = {
                    "name": self._category_names[cat],
                    "items": []
                }
            groups[cat]["items"].append({
                "source": src,
                "target": dst,
                "label": f"{src.upper()} 转 {dst.upper()}"
            })
        return groups


# 全局实例 + 装饰器别名
registry = ConverterRegistry()
register_converter = registry.register
