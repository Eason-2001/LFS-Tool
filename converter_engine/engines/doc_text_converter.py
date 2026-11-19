#!/usr/bin/env python3
# coding=utf-8
# @Time    :2026/11/19 15:00
# @Author  :liufushuang
# 纯 Python 可完成的文档/文本互转，不依赖外部渲染引擎
from .base import BaseConverter
from .registry import register_converter
from docx import Document
from docx.oxml.ns import qn
from docx.shared import Cm


def _normalize_docx_fonts(doc, west="Calibri", east="微软雅黑"):
    """后处理：把所有文字统一为通用字体。

    源 PDF 里引用的字体（如阿里巴巴普惠体）在用户机器上往往没装，
    保留原字体名会导致打开时回退到默认字体、字宽换行错位；
    统一成 Windows/WPS 常见字体，显示更稳定。字号与加粗层级保持不变。
    """
    def fix_runs(runs):
        for r in runs:
            rpr = r._element.get_or_add_rPr()
            rf = rpr.find(qn("w:rFonts"))
            if rf is None:
                rf = rpr.makeelement(qn("w:rFonts"), {})
                rpr.insert(0, rf)
            rf.set(qn("w:ascii"), west)
            rf.set(qn("w:hAnsi"), west)
            rf.set(qn("w:eastAsia"), east)

    for p in doc.paragraphs:
        fix_runs(p.runs)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    fix_runs(p.runs)


def _normalize_page_margins(doc, margin_cm=2.5):
    """后处理：把页面边距设回正常值。

    pdf2docx 转出的文档边距常被置为 0，内容会顶到纸张边缘、右侧被截断；
    统一补回四周留白。
    """
    for sec in doc.sections:
        sec.left_margin = Cm(margin_cm)
        sec.right_margin = Cm(margin_cm)
        sec.top_margin = Cm(margin_cm)
        sec.bottom_margin = Cm(margin_cm)


def _remove_empty_rows(doc):
    """删除表格中所有单元格都为空的占位行。"""
    for table in doc.tables:
        for row in list(table.rows):
            if not any(cell.text.strip() for cell in row.cells):
                row._tr.getparent().remove(row._tr)


def _merge_split_header_tables(doc):
    """合并被拆开的表头表与紧随其后的同列数数据表。

    pdf2docx 偶尔把"表头行"和"数据行"识别成两个独立表格，这里把仅含一行、
    且与下一表格列数相同的前表，与后表拼接为一张表。
    """
    body = doc.element.body
    tbls = body.findall(qn("w:tbl"))

    def row_count(tbl):
        return len(tbl.findall(qn("w:tr")))

    def col_count(tbl):
        grid = tbl.find(qn("w:tblGrid"))
        return len(grid.findall(qn("w:gridCol"))) if grid is not None else 0

    i = 0
    while i < len(tbls) - 1:
        a, b = tbls[i], tbls[i + 1]
        if row_count(a) == 1 and col_count(a) == col_count(b) and col_count(a) > 0:
            for tr in b.findall(qn("w:tr")):
                a.append(tr)
            body.remove(b)
            tbls = body.findall(qn("w:tbl"))
            continue
        i += 1


def _remove_grid_background_images(doc):
    """后处理：删除被渲染成位图的表格网格背景图。

    pdf2docx 有时不把表格边框写成 Word 边框，而是把整张数据表的横竖网格
    渲染成一张白底浅灰线的 PNG 叠在文字下方。这类图几乎全白、不含任何
    深色像素（没有文字/照片内容），据此识别并移除，避免出现多余的表格框。
    真实截图、照片含深色或彩色内容，不会被误删。
    """
    import io
    from PIL import Image

    def is_grid_background(blob):
        try:
            im = Image.open(io.BytesIO(blob)).convert("RGB")
            im.thumbnail((300, 300))
            pixels = list(im.getdata())
            total = len(pixels)
            if total == 0:
                return False
            white = sum(1 for p in pixels if p[0] > 245 and p[1] > 245 and p[2] > 245)
            dark = sum(1 for p in pixels if p[0] < 120 and p[1] < 120 and p[2] < 120)
            return white / total > 0.90 and dark == 0
        except Exception:
            return False

    part = doc.part
    for drawing in list(doc.element.body.iter(qn("w:drawing"))):
        blip = drawing.find(".//" + qn("a:blip"))
        if blip is None:
            continue
        rid = blip.get(qn("r:embed"))
        if not rid or rid not in part.related_parts:
            continue
        if is_grid_background(part.related_parts[rid].blob):
            drawing.getparent().remove(drawing)


@register_converter
class PdfToDocxConverter(BaseConverter):
    """PDF → DOCX（排版还原受 pdf2docx 能力限制，复杂表格/多栏可能有偏差）"""
    category = "document"
    category_name = "文档格式转换"

    @staticmethod
    def supports():
        return [("pdf", "docx")]

    def convert(self, input_path: str, output_path: str):
        from pdf2docx import Converter
        cv = Converter(input_path)
        try:
            cv.convert(output_path)
        finally:
            cv.close()
        # 后处理：统一通用字体、补回页边距、清理表格空行、合并拆开的表头表、移除网格背景图
        doc = Document(output_path)
        _normalize_docx_fonts(doc)
        _normalize_page_margins(doc)
        _remove_empty_rows(doc)
        _merge_split_header_tables(doc)
        _remove_grid_background_images(doc)
        doc.save(output_path)


@register_converter
class DocxToTxtConverter(BaseConverter):
    """DOCX → TXT：提取段落文字，存为纯文本"""
    category = "document"
    category_name = "文档格式转换"

    @staticmethod
    def supports():
        return [("docx", "txt")]

    def convert(self, input_path: str, output_path: str):
        from docx import Document
        doc = Document(input_path)
        lines = [paragraph.text for paragraph in doc.paragraphs]
        text = "\n".join(lines)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)


@register_converter
class PdfToTxtConverter(BaseConverter):
    """PDF → TXT：提取页面文字，存为纯文本（扫描件无文字层时结果为空）"""
    category = "document"
    category_name = "文档格式转换"

    @staticmethod
    def supports():
        return [("pdf", "txt")]

    def convert(self, input_path: str, output_path: str):
        import pymupdf
        doc = pymupdf.open(input_path)
        try:
            parts = [page.get_text() for page in doc]
        finally:
            doc.close()
        text = "\n".join(parts)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)


@register_converter
class TxtToDocxConverter(BaseConverter):
    """TXT → DOCX：每行文字写入一个段落，生成新的 Word 文档"""
    category = "document"
    category_name = "文档格式转换"

    @staticmethod
    def supports():
        return [("txt", "docx")]

    def convert(self, input_path: str, output_path: str):
        from docx import Document
        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()
        doc = Document()
        for line in text.splitlines():
            doc.add_paragraph(line)
        doc.save(output_path)
