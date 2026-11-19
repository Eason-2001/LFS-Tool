#!/usr/bin/env python3
# coding=utf-8
# @Time    :2026/11/19 15:10
# @Author  :liufushuang
# 依赖本机 LibreOffice(soffice) headless 完成 DOCX → PDF
import os
import shutil
import subprocess
import tempfile

from .base import BaseConverter
from .registry import register_converter


@register_converter
class DocxToPdfConverter(BaseConverter):
    """DOCX → PDF：调用本机 LibreOffice headless 渲染，需先安装 libreoffice 与中文字体"""
    category = "document"
    category_name = "文档格式转换"

    @staticmethod
    def supports():
        return [("docx", "pdf")]

    def _find_soffice(self):
        # 不同发行版命令名可能是 soffice 或 libreoffice
        return shutil.which("soffice") or shutil.which("libreoffice")

    def convert(self, input_path: str, output_path: str):
        soffice = self._find_soffice()
        if not soffice:
            raise RuntimeError("未检测到 LibreOffice(soffice)，请先安装后再使用 DOCX→PDF 转换")

        out_dir = os.path.dirname(os.path.abspath(output_path))
        os.makedirs(out_dir, exist_ok=True)

        # 每次转换用独立 user profile，避免多进程共用配置目录产生文件锁冲突
        profile_dir = tempfile.mkdtemp(prefix="lo_profile_")
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        expected_pdf = os.path.join(out_dir, base_name + ".pdf")

        cmd = [
            soffice,
            f"-env:UserInstallation=file://{profile_dir}",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", out_dir,
            input_path,
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=90
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("转换超时（超过 90 秒），请稍后重试")
        finally:
            shutil.rmtree(profile_dir, ignore_errors=True)

        if result.returncode != 0:
            raise RuntimeError(f"LibreOffice 转换失败：{result.stderr.strip() or result.stdout.strip()}")

        if not os.path.exists(expected_pdf):
            raise RuntimeError("LibreOffice 未生成 PDF 文件，请检查源文档是否正常")

        # soffice 按输入文件名输出，这里移动到接口约定的目标路径
        if os.path.abspath(expected_pdf) != os.path.abspath(output_path):
            shutil.move(expected_pdf, output_path)
