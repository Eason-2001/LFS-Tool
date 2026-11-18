#!/usr/bin/env python3
# coding=utf-8
# @Time    :2026/11/17 13:47
# @Author  :liufushuang
# apps/converter/urls.py
from django.urls import path
from .views import SupportedFormatView
from .views import SupportedFormatView, FileConvertView,FileDownloadView

urlpatterns = [
    path("supported/", SupportedFormatView.as_view(), name="supported"),
    path("convert/", FileConvertView.as_view(), name="convert"),
    path("download/<str:filename>/", FileDownloadView.as_view(), name="download"),
]
