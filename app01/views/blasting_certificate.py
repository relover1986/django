from django.shortcuts import render, HttpResponse, redirect
import time
import torch
import torch.nn as nn
import json
import tempfile
import cv2
from rapidocr_onnxruntime import RapidOCR
from django.http import JsonResponse
from app01 import models
from app01.models import UploadedZhaopian
from app01 import modelform
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import zipfile
import io
from app01.services import export_service
from collections import defaultdict
from app01.jiami import md5
from app01.func import *
from app01.photo import *
from django_filters.views import FilterView
from django.views.generic import ListView
import pandas as pd
from openpyxl import load_workbook
import os
from docx import Document
import sqlite3 as sl
from django.shortcuts import render
from django.apps import apps
from app01.models import ExplosiveInventoryItem
from app01.modelform import ExplosiveInventoryItemForm
from PIL import Image
import io
import os
from django.core.files.base import ContentFile
from openpyxl import Workbook
from PIL import Image
from openpyxl.drawing.image import Image as ExcelImage
import base64
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
from django.conf import settings
import uuid
import json
import sys
sys.path.insert(0, "/root/django")
import utils
import sys
sys.path.insert(0, "/root/django")
import utils

from openpyxl import Workbook
from django.http import HttpResponse
import io
from datetime import datetime


import zipfile
from io import BytesIO

from aip import AipBodyAnalysis
import base64
import io
from PIL import Image
import os
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
# 百度API配置
APP_ID = '118049497'
API_KEY = 'AmK3oZpZhns9jAm2rJgzRyLq'
SECRET_KEY = 'LbbCCzQyv1FlytQxBHstZ5Yt5i4B7pMw'
client = AipBodyAnalysis(APP_ID, API_KEY, SECRET_KEY)


def blastingcertificate_add(request):
    title = 'tu'
    if request.method == 'POST':
        files = request.FILES.getlist('file')
        for file in files:
            time.sleep(0.1)
            with Image.open(file) as img:
                if img.mode in ('RGBA', 'LA'):
                    img = img.convert('RGB')

                filename = request.POST['name']
                certificate_number = request.POST['certificate_number']
                # 设置目标尺寸
                target_size = (2067, 1476)
                a4_size = (2480, 3508)

                # 调整图片尺寸
                img = img.resize(target_size, Image.LANCZOS)

                # 创建A4画布并居中放置图片
                a4_bg = Image.new('RGB', a4_size, (255, 255, 255))
                x = (a4_size[0] - target_size[0]) // 2
                y = (a4_size[1] - target_size[1]) // 2
                a4_bg.paste(img, (x, y))

                # 保存处理后的图片
                img_io = io.BytesIO()
                a4_bg.save(img_io, format='JPEG', quality=95)
                img_bytes = img_io.getvalue()

                # 直接保存A4排版后的图片（移除背景生成逻辑）
                rotated_io = io.BytesIO()
                a4_bg.save(rotated_io, format='JPEG', quality=95)
                rotated_bytes = rotated_io.getvalue()

                # 更新模型保存字段
                models.BlastingCertificate.objects.create(
                    name=filename,
                    certificate_number=certificate_number,

                    certificate_photo=ContentFile(
                        rotated_bytes, name=f"{filename}_rotated.jpg"),

                )

        return redirect("/home/blastingcertificate_list")
    else:
        model_names = models.BlastingCertificate.objects.values_list(
            'name', flat=True).distinct()
        return render(request, 'blastingcertificate_add.html', {'model_names': model_names})


def blastingcertificate_delete(request):

    id = request.GET.get('id')
    models.BlastingCertificate.objects.filter(id=str(id)).delete()
    return redirect("/home/blastingcertificate_list")


def blastingcertificate_list(request):

    title = 'blastingcertificate'
    if request.method == "GET":
        model_fields = models.BlastingCertificate._meta.fields
        cols = [{'verbose_name': field.verbose_name} for field in model_fields if field.attname not in ('id', 'location')]
        cols.append({'verbose_name': '操作'})
        data = models.BlastingCertificate.objects.values("name", "photo", "rotated_photo", "blue_background", "red_background", "white_background", "uploaded_at").order_by(
            '-created_at')[:100]
        return render(request, 'blastingcertificate_list.html', {
            "data": data,
            "cols": cols,
            "title": title,
            "export_url": "/home/blastingcertificate_export_zip",  # 新增导出URL参数
            "export_xlsx_url": "/home/blastingcertificate_export_xlsx"  # 新增Excel导出参数
        })


@require_role("爆破工程技术人员", "资料员")
def blastingcertificate_export_xlsx(request):
    from datetime import datetime

    excel_io = export_service.blastingcertificate_export_xlsx()
    response = HttpResponse(
        excel_io.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"blasting_certs_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@require_role("爆破工程技术人员", "资料员")
def blastingcertificate_export_zip(request):
    zip_buffer = export_service.blastingcertificate_export_zip()
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="blasting_certificates.zip"'
    return response


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
