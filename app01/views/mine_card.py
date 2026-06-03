from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
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


import os
from io import BytesIO

from django.contrib import messages
from django.db import transaction

from app01.forms import WorkerForm, ExcelUploadForm, PhotoForm
from app01.image_utils import (
    generate_label,
    generate_back_label,
    generate_sheets,
    generate_zip,
)


def mine_card_index(request):
    """首页：Excel 导入 + 人员列表 + 逐行照片上传"""
    dept = request.session.get("info", {}).get("department", "")
    workers = models.Worker.objects.all().order_by("id")
    if dept:
        workers = workers.filter(department=dept)
    excel_form = ExcelUploadForm()
    worker_form = WorkerForm(initial={"job_type": ""})

    if request.method == "POST" and "excel" in request.FILES:
        excel_form = ExcelUploadForm(request.POST, request.FILES)
        if excel_form.is_valid():
            try:
                imported = _mine_card_parse_excel(request.FILES["excel"], department=dept)
                messages.success(request, f"成功导入 {imported} 人")
                return redirect("mine_card_index")
            except Exception as e:
                messages.error(request, f"导入失败：{e}")

    if request.method == "POST" and "name" in request.POST:
        worker_form = WorkerForm(request.POST, request.FILES)
        if worker_form.is_valid():
            worker = worker_form.save(commit=False)
            if dept:
                worker.department = dept
            worker.save()
            messages.success(request, "已添加")
            return redirect("mine_card_index")

    job_types = list(models.JobType.objects.values_list("name", flat=True).order_by("name"))
    return render(request, "mine_card/upload.html", {
        "workers": workers,
        "excel_form": excel_form,
        "worker_form": worker_form,
        "photo_forms": {w.id: PhotoForm(instance=w) for w in workers},
        "worker_names_json": json.dumps(list(models.Worker.objects.values_list("name", flat=True).distinct().order_by("name"))),
        "job_type_choices_json": json.dumps(job_types),
        "job_types": job_types,
    })


def mine_card_delete(request, worker_id):
    """删除人员"""
    worker = get_object_or_404(models.Worker, id=worker_id)
    if worker.photo and os.path.exists(worker.photo.path):
        os.remove(worker.photo.path)
    worker.delete()
    return redirect("mine_card_index")

@csrf_exempt
def mine_card_batch_delete(request):
    """批量删除人员"""
    if request.method == "POST":
        ids = request.POST.get("ids", "")
        if ids:
            id_list = [i.strip() for i in ids.split(",") if i.strip().isdigit()]
            workers = models.Worker.objects.filter(id__in=id_list)
            for w in workers:
                if w.photo and os.path.exists(w.photo.path):
                    os.remove(w.photo.path)
            deleted, _ = workers.delete()
            return JsonResponse({"code": 200, "deleted": deleted})
    return JsonResponse({"error": "invalid request"}, status=400)

def mine_card_update_photo(request, worker_id):
    """单行上传照片 → 固定一寸标准 295×413，JPEG quality=45，清 EXIF"""
    from io import BytesIO
    from PIL import Image

    worker = get_object_or_404(models.Worker, id=worker_id)
    if request.method == "POST" and "photo" in request.FILES:
        from django.core.files.uploadedfile import InMemoryUploadedFile

        uploaded = request.FILES["photo"]
        img = Image.open(uploaded)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # 等比缩放覆盖 295×413，再中心裁剪
        tw, th = 295, 413
        w, h = img.size
        scale = max(tw / w, th / h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        left = (img.width - tw) // 2
        top = (img.height - th) // 2
        img = img.crop((left, top, left + tw, top + th))

        buf = BytesIO()
        img.save(buf, format="JPEG", quality=45,
                 optimize=True, subsampling="4:2:0")
        buf.seek(0)
        request.FILES["photo"] = InMemoryUploadedFile(
            buf, "photo", uploaded.name, "image/jpeg",
            buf.getbuffer().nbytes, None
        )

        form = PhotoForm(request.POST, request.FILES, instance=worker)
        if form.is_valid():
            form.save()
    return redirect("mine_card_index")


def _mine_card_workers_with_photos(department=None):
    """返回有有效照片文件的人员列表（DB 记录 + 文件都存在）"""
    from app01.services.card_service import get_workers_with_photos
    return get_workers_with_photos(department=department)


def mine_card_preview(request):
    """A4 排版预览页"""
    dept = request.session.get("info", {}).get("department", "")
    workers = _mine_card_workers_with_photos(department=dept)
    if not workers:
        messages.warning(request, "请先上传照片")
        return redirect("mine_card_index")

    front_bufs, back_bufs = _mine_card_generate_all_cards(workers)
    sheets = generate_sheets(workers, front_bufs, back_bufs)

    return render(request, "mine_card/preview.html", {
        "sheets": sheets,
        "total": len(workers),
    })


def mine_card_download(request):
    """下载 A4 排版 ZIP"""
    dept = request.session.get("info", {}).get("department", "")
    workers = _mine_card_workers_with_photos(department=dept)
    if not workers:
        return redirect("mine_card_index")

    front_bufs, back_bufs = _mine_card_generate_all_cards(workers)
    zip_buf = generate_zip(workers, front_bufs, back_bufs)

    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    response = HttpResponse(zip_buf, content_type="application/zip")
    response["Content-Disposition"] = f'attachment; filename="入井标签_A4排版_{timestamp}.zip"'
    return response


def _mine_card_parse_excel(excel_file, department=""):
    """解析 Excel，返回导入数量"""
    from app01.services.card_service import parse_excel
    return parse_excel(excel_file, department=department)


def _mine_card_generate_all_cards(workers):
    """为所有人生成正反面单卡 BytesIO"""
    from app01.services.card_service import generate_all_cards
    return generate_all_cards(workers)
