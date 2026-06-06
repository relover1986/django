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


def home(request):
    return render(request, "home.html")


def department_quiz_stats(request):
    """本部门答题统计"""
    import qrcode
    import io
    import base64
    from collections import defaultdict

    # 答题专用二维码（这个页面也显示二维码，方便扫码）
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data("http://bxks.online/staff_login/")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    qr_base64 = base64.b64encode(buf.getvalue()).decode()

    # 本部门答题统计
    dept_stats = []
    info = request.session.get("info", {})
    ident = info.get("ident", "")
    dept = info.get("department", "")
    is_admin = ident in ("000001", "000002")

    if is_admin:
        # 管理员：看全部部门
        staff_list = models.Staff.objects.filter(status="在职").order_by("department", "name")
    elif dept:
        staff_list = models.Staff.objects.filter(department=dept, status="在职")
    else:
        staff_list = []

    if staff_list:
        total_baopo = models.Question.objects.filter(category="爆破").count()
        total_jingong = models.Question.objects.filter(category="井工").count()
        total_weizhuang = models.Question.objects.filter(category="危装").count()

        for staff in staff_list:
            phone = staff.phone
            score_baopo = models.UserAnswer.objects.filter(ident=phone, ti_type="爆破").count()
            score_jingong = models.UserAnswer.objects.filter(ident=phone, ti_type="非煤矿山井工").count()
            score_weizhuang = models.UserAnswer.objects.filter(ident=phone, ti_type="危险品装卸").count()
            remain_baopo = total_baopo - score_baopo
            remain_jingong = total_jingong - score_jingong
            remain_weizhuang = total_weizhuang - score_weizhuang
            dept_stats.append({
                "name": staff.name,
                "phone": phone,
                "dept": staff.department if is_admin else "",
                "score_baopo": score_baopo,
                "remain_baopo": remain_baopo,
                "score_jingong": score_jingong,
                "remain_jingong": remain_jingong,
                "score_weizhuang": score_weizhuang,
                "remain_weizhuang": remain_weizhuang,
            })
        dept_stats.sort(key=lambda x: x["remain_baopo"] + x["remain_jingong"] + x["remain_weizhuang"], reverse=True)

    return render(request, "department_quiz_stats.html", {
        "qr_base64": qr_base64,
        "dept_stats": dept_stats,
        "dept_name": "全部部门" if is_admin else dept,
        "is_admin": is_admin,
        "active_type": request.GET.get("type", ""),
    })

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



# Vue 前端入口
def vue_app(request, vue_path=None):
    from django.shortcuts import render
    return render(request, 'vue/index.html')
