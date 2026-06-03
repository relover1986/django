from django.shortcuts import render, HttpResponse, redirect
import time
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
from app01.services.blasting_site_service import SignNetMulti, _load_sign_model, 识别签名, _preprocess_signature, _train_sse_events


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


def blasting_site_photo_list(request):
    title = 'blasting_site_photo'
    if request.method == 'GET':
        from app01 import models
        model_fields = models.BlastingSitePhoto._meta.fields
        cols = [{'verbose_name': field.verbose_name} for field in model_fields if field.attname not in ('id', 'location')]
        cols.append({'verbose_name': '操作'})
        data = models.BlastingSitePhoto.objects.values("name", "photo", "rotated_photo", "blue_background", "red_background", "white_background", "uploaded_at").order_by('code')[:100]
        return render(request, 'blasting_site_photo_list.html', {
            'data': data,
            'cols': cols,
            'title': title,
        })



def blasting_site_photo_add(request):
    title = 'blasting_site_photo'
    if request.method == 'POST':
        from app01 import models
        import cv2, tempfile, os
        import numpy as np
        from django.core.files.base import ContentFile
        from deskew import determine_skew

        ocr_engine = RapidOCR()
        files = request.FILES.getlist('file')
        location = request.POST.get('location', '')
        blaster = request.POST.get('blaster', '')
        safety_officer = request.POST.get('safety_officer', '')
        engineer = request.POST.get('engineer', '')

        def 回正(img):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            angle = determine_skew(gray)
            h, w = img.shape[:2]
            M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
            return cv2.warpAffine(img, M, (w, h),
                                  flags=cv2.INTER_CUBIC,
                                  borderMode=cv2.BORDER_REPLICATE)

        def 处理单张(img):
            ident = ''
            # Step 1: 回正
            img = 回正(img)
            h, w = img.shape[:2]
            # Step 2: OCR全图定位关键文字
            _, tmp = tempfile.mkstemp(suffix='.jpg')
            cv2.imwrite(tmp, img)
            result, _ = ocr_engine(tmp)
            os.unlink(tmp)

            top_y, left_x, bottom_y = 0, 0, h
            for box, text, conf in result or []:
                pts = np.array(box, dtype=np.int32)
                xs = pts[:, 0]
                ys = pts[:, 1]
                if '爆破现场记录' in text:
                    ident = text.split("录")[1].zfill(7)
                    top_y = int(ys.min())
                if '作业场地' in text:
                    left_x = int(xs.min())
                if '存根' in text:
                    bottom_y = int(ys.max())

            # Step 3: 根据 OCR 定位裁图
            top_y = max(top_y, 0)
            left_x = max(left_x, 0)
            bottom_y = min(bottom_y, h)
            if bottom_y - top_y >= 10 and w - left_x >= 10:
                img = img[top_y:bottom_y, left_x:w]
            return img, ident

        for file in files:
            time.sleep(0.1)
            file_bytes = np.frombuffer(file.read(), np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            if img is None:
                file.seek(0)
                models.BlastingSitePhoto.objects.create(
                    location=location, photo=file, code='',
                    blaster=blaster, safety_officer=safety_officer, engineer=engineer
                )
                continue

            processed_img, ident = 处理单张(img)

            # 统一高度为 1200px（等比例缩放）
            h, w = processed_img.shape[:2]
            if h != 1200:
                new_w = int(w * 1200 / h)
                processed_img = cv2.resize(processed_img, (new_w, 1200), interpolation=cv2.INTER_LANCZOS4)

            # ── 签名识别 ──
            sig_result, low_conf_list = 识别签名(ocr_engine, processed_img)
            if low_conf_list:
                print(f"[签名] {len(low_conf_list)} 张低置信度裁图 -> {LOW_CONF_DIR}")

            # RapidOCR 定位"爆破现场记录"文字块，右侧+50像素裁切
            _, _tmp2 = tempfile.mkstemp(suffix='.jpg')
            cv2.imwrite(_tmp2, processed_img)
            _res2, _ = ocr_engine(_tmp2)
            os.unlink(_tmp2)
            _crop_right = processed_img.shape[1]
            for _box, _text, _conf in _res2 or []:
                if '爆破现场记录' in _text:
                    _pts = np.array(_box, dtype=np.int32)
                    _crop_right = min(int(_pts[:, 0].max()) + 50, processed_img.shape[1])
                    break
            processed_img = processed_img[:, :_crop_right]

            # JPEG压缩 quality=82
            success, encoded = cv2.imencode('.jpg', processed_img, [cv2.IMWRITE_JPEG_QUALITY, 82])
            if success:
                name = file.name.rsplit('.', 1)[0] + '.jpg'
                models.BlastingSitePhoto.objects.create(
                    location=location,
                    photo=ContentFile(encoded.tobytes(), name=name),
                    code=ident,
                    blaster=sig_result.get('blaster', ''),
                    safety_officer=sig_result.get('safety_officer', ''),
                    engineer=sig_result.get('engineer', ''),
                )
            else:
                file.seek(0)
                models.BlastingSitePhoto.objects.create(
                    location=location, photo=file, code=ident,
                    blaster=sig_result.get('blaster', ''),
                    safety_officer=sig_result.get('safety_officer', ''),
                    engineer=sig_result.get('engineer', ''),
                )

        return redirect('/home/blasting_site_photo_list')

    return render(request, 'blasting_site_photo_add.html')



def blasting_site_low_conf(request):
    """低置信度签名裁图列表"""
    import os, json
    from django.conf import settings
    low_dir = os.path.join(settings.MEDIA_ROOT, "blasting_site_low_conf")
    files = []
    if os.path.isdir(low_dir):
        for fname in sorted(os.listdir(low_dir), reverse=True):
            fpath = os.path.join(low_dir, fname)
            if os.path.isfile(fpath):
                size = os.path.getsize(fpath)
                files.append({'name': fname, 'size': size})
    # 读取 label_map.json 作为姓名下拉选项
    label_map_path = '/root/MLX/05模型文件/label_map.json'
    name_options = []
    try:
        with open(label_map_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for v in data.values("name", "photo", "rotated_photo", "blue_background", "red_background", "white_background", "uploaded_at"):
                if v.strip():
                    name_options.append(v.strip())
    except Exception:
        name_options = []
    return render(request, 'blasting_site_low_conf.html', {'files': files, 'name_options': name_options})


def blasting_site_photo_delete(request):
    id = request.GET.get('id')
    from app01 import models
    models.BlastingSitePhoto.objects.filter(id=str(id)).delete()
    return redirect('/home/blasting_site_photo_list')

def blasting_site_low_conf_delete(request):
    """删除低置信度签名裁图"""
    import os
    from django.conf import settings
    from django.shortcuts import redirect
    filename = request.GET.get('filename')
    if filename:
        fpath = os.path.join(settings.MEDIA_ROOT, 'blasting_site_low_conf', filename)
        if os.path.isfile(fpath):
            os.remove(fpath)
    return redirect('/home/blasting_site_low_conf/')


def blasting_site_low_conf_submit(request):
    """提交低置信度裁图到对应签名文件夹"""
    import os, json
    from django.conf import settings
    from django.http import JsonResponse
    from django.views.decorators.csrf import csrf_exempt

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': '仅支持POST'})

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'JSON解析失败'})

    items = data.get('items', [])
    if not items:
        return JsonResponse({'success': False, 'message': '没有提交项'})

    src_dir = os.path.join(settings.MEDIA_ROOT, 'blasting_site_low_conf')
    dst_root = os.path.join(settings.MEDIA_ROOT, '签名')
    moved = 0
    errors = []

    for item in items:
        filename = item.get('filename', '').strip()
        name = item.get('name', '').strip()
        if not filename or not name:
            errors.append(f'{filename or "?"}: 姓名列为空')
            continue

        src_path = os.path.join(src_dir, filename)
        if not os.path.isfile(src_path):
            errors.append(f'{filename}: 源文件不存在')
            continue

        dst_dir = os.path.join(dst_root, name)
        os.makedirs(dst_dir, exist_ok=True)

        dst_path = os.path.join(dst_dir, filename)
        if os.path.exists(dst_path):
            base, ext = os.path.splitext(filename)
            import time
            dst_path = os.path.join(dst_dir, f'{base}_{int(time.time())}{ext}')

        os.rename(src_path, dst_path)
        moved += 1

    return JsonResponse({
        'success': True,
        'moved': moved,
        'errors': errors,
    })



def blasting_site_train_signatures(request):
    from django.http import StreamingHttpResponse
    response = StreamingHttpResponse(_train_sse_events(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


# ============================================================
# 人员管理（新）— Staff / CertType / StaffCert / StaffCertFile
# ============================================================
