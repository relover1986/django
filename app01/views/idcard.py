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


def idcard_add(request):
    title = 'tu'

    if request.method == 'POST':
        import cv2, numpy as np
        from PIL import Image
        import io
        from microwink import SegModel

        # ---- 接收两张图 ----
        front_file = request.FILES.get('人像')
        back_file = request.FILES.get('国徽')
        if not front_file or not back_file:
            return JsonResponse({'error': '请同时选择人像面和国徽面的图片'}, status=400)

        # ---- microwink 回正函数 ----
        def straighten(uploaded_file):
            from app01.services.idcard_service import straighten_idcard
            return straighten_idcard(uploaded_file)

        # ---- 两张各自回正 ----
        try:
            img_人像 = straighten(front_file)
            img_国徽 = straighten(back_file)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)

        # ---- OCR（用人像面） ----
        straightened_file = io.BytesIO(img_人像)
        straightened_file.name = 'straightened.jpg'

        姓名, 身份证号码 = sfz(straightened_file)

        if not 姓名 or not 身份证号码 or '未知' in str(姓名) or '未知' in str(身份证号码):
            return JsonResponse({'error': '未识别出身份证信息，请确保人像面清晰完整后重试'}, status=400)

        # ---- 双面合成图 ----
        img1_pil = Image.open(io.BytesIO(img_人像))
        img2_pil = Image.open(io.BytesIO(img_国徽))
        combined_img = combine_a4_images(img1_pil, img2_pil)
        buf = io.BytesIO()
        combined_img.save(buf, format='JPEG', quality=90)
        combined_bytes = buf.getvalue()

        # ---- 入库 ----
        models.IDCard.objects.create(
            name=姓名,
            id_number=身份证号码,
            front_image=ContentFile(img_人像, name=f"{身份证号码}.jpg"),
            back_image=ContentFile(img_国徽, name=f"{身份证号码}_rotated.jpg"),
            combined_image=ContentFile(combined_bytes, name=f"{身份证号码}_双面.jpg"),
        )

        return redirect("/home/idcard_list")

    else:
        model_names = models.IDCard.objects.values_list('name', flat=True).distinct()
        return render(request, 'idcard_add.html', {'model_names': model_names})


def idcard_delete(request):

    id = request.GET.get('id')
    models.IDCard.objects.filter(id=str(id)).delete()
    return redirect("/home/idcard_list")


@csrf_exempt
def api_idcard_add(request):
    if request.method == 'POST':
        try:
            front_file = request.FILES.get('front')
            back_file = request.FILES.get('back')
            upload_id = request.POST.get('upload_id')

            # 支持分步上传：使用UUID关联两次上传
            if front_file and not back_file:
                # 只上传了人像面，进行OCR识别并存储到临时文件
                with Image.open(front_file) as img1:
                    img1 = resize_photo(img1, 3)
                    if img1.mode == 'RGBA':
                        img1 = img1.convert('RGB')

                    img_io = io.BytesIO()
                    img1.save(img_io, format='JPEG')
                    img_人像 = img_io.getvalue()

                姓名, 身份证号码 = sfz(front_file)

                # 生成唯一的上传ID
                upload_id = str(uuid.uuid4())

                # 将数据存储到临时文件
                temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
                os.makedirs(temp_dir, exist_ok=True)

                temp_file_path = os.path.join(temp_dir, f"{upload_id}.json")
                temp_data = {
                    'name': 姓名,
                    'id_number': 身份证号码,
                    'front_image': base64.b64encode(img_人像).decode('utf-8'),
                    'front_filename': f"{身份证号码}.jpg"
                }

                with open(temp_file_path, 'w', encoding='utf-8') as f:
                    json.dump(temp_data, f)

                return JsonResponse({
                    'success': True,
                    'message': '人像面上传成功',
                    'data': {
                        'name': 姓名,
                        'id_number': 身份证号码,
                        'upload_id': upload_id
                    }
                })

            elif not front_file and back_file and upload_id:
                # 只上传了国徽面，检查临时文件中是否有人像面数据
                temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
                temp_file_path = os.path.join(temp_dir, f"{upload_id}.json")

                if not os.path.exists(temp_file_path):
                    return JsonResponse({
                        'success': False,
                        'message': '请先上传人像面'
                    }, status=400)

                # 读取临时文件
                with open(temp_file_path, 'r', encoding='utf-8') as f:
                    idcard_upload = json.load(f)

                # 处理国徽面
                with Image.open(back_file) as img2:
                    img2 = resize_photo(img2, 3)
                    if img2.mode == 'RGBA':
                        img2 = img2.convert('RGB')

                    img_io = io.BytesIO()
                    img2.save(img_io, format='JPEG')
                    img_国徽 = img_io.getvalue()

                # 从临时文件中获取人像面数据（将base64字符串转换回字节数据）
                img_人像 = base64.b64decode(idcard_upload['front_image'])
                姓名 = idcard_upload['name']
                身份证号码 = idcard_upload['id_number']

                # 重新打开人像面图片用于合并
                with Image.open(io.BytesIO(img_人像)) as img1:
                    combined_img = combine_a4_images(img1, img2)

                    img_io = io.BytesIO()
                    combined_img.save(img_io, format='JPEG', quality=90)
                    combined_bytes = img_io.getvalue()

                # 保存到数据库
                idcard = models.IDCard.objects.create(
                    name=姓名,
                    id_number=身份证号码,
                    front_image=ContentFile(img_人像, name=f"{身份证号码}.jpg"),
                    back_image=ContentFile(
                        img_国徽, name=f"{身份证号码}_rotated.jpg"),
                    combined_image=ContentFile(
                        combined_bytes, name=f"{身份证号码}_双面.jpg")
                )

                # 删除临时文件
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

                return JsonResponse({
                    'success': True,
                    'message': '身份证上传成功',
                    'data': {
                        'id': idcard.id,
                        'name': 姓名,
                        'id_number': 身份证号码,
                        'created_at': idcard.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    }
                })

            elif not front_file or not back_file:
                return JsonResponse({
                    'success': False,
                    'message': '请上传人像面和国徽面图片'
                }, status=400)

            with Image.open(front_file) as img1:
                img1 = resize_photo(img1, 3)
                if img1.mode == 'RGBA':
                    img1 = img1.convert('RGB')

                img_io = io.BytesIO()
                img1.save(img_io, format='JPEG')
                img_人像 = img_io.getvalue()

            with Image.open(back_file) as img2:
                img2 = resize_photo(img2, 3)
                if img2.mode == 'RGBA':
                    img2 = img2.convert('RGB')

                img_io = io.BytesIO()
                img2.save(img_io, format='JPEG')
                img_国徽 = img_io.getvalue()

            combined_img = combine_a4_images(img1, img2)

            img_io = io.BytesIO()
            combined_img.save(img_io, format='JPEG', quality=90)
            combined_bytes = img_io.getvalue()

            姓名, 身份证号码 = sfz(front_file)

            idcard = models.IDCard.objects.create(
                name=姓名,
                id_number=身份证号码,
                front_image=ContentFile(img_人像, name=f"{身份证号码}.jpg"),
                back_image=ContentFile(img_国徽, name=f"{身份证号码}_rotated.jpg"),
                combined_image=ContentFile(
                    combined_bytes, name=f"{身份证号码}_双面.jpg")
            )

            return JsonResponse({
                'success': True,
                'message': '身份证上传成功',
                'data': {
                    'id': idcard.id,
                    'name': 姓名,
                    'id_number': 身份证号码,
                    'created_at': idcard.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'上传失败: {str(e)}'
            }, status=500)

    return JsonResponse({
        'success': False,
        'message': '请使用 POST 方法'
    }, status=405)


@csrf_exempt
def api_idcard_list(request):
    if request.method == 'GET':
        try:
            idcards = models.IDCard.objects.all().order_by('-created_at')[:100]
            result_list = []
            for card in idcards:
                created_at_str = ''
                if card.created_at:
                    try:
                        created_at_str = card.created_at.strftime(
                            '%Y-%m-%d %H:%M:%S')
                    except:
                        created_at_str = str(card.created_at)

                result_list.append({
                    'id': card.id,
                    'name': card.name,
                    'id_number': card.id_number,
                    'created_at': created_at_str,
                    'front_image': card.front_image.url if card.front_image else '',
                    'back_image': card.back_image.url if card.back_image else '',
                    'combined_image': card.combined_image.url if card.combined_image else ''
                })

            return JsonResponse({
                'success': True,
                'data': result_list
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': f'获取列表失败: {str(e)}'
            }, status=500)

    return JsonResponse({
        'success': False,
        'message': '请使用 GET 方法'
    }, status=405)


def idcard_list(request):

    title = 'idcard'
    if request.method == "GET":
        model_fields = models.IDCard._meta.fields
        cols = [{'verbose_name': field.verbose_name} for field in model_fields if field.attname not in ('id', 'location')]
        cols.append({'verbose_name': '操作'})
        data = models.IDCard.objects.values("name", "id_number", "front_image", "back_image", "combined_image", "created_at").order_by('-created_at')[:100]
        return render(request, 'idcard_list.html', {
            "data": data,
            "cols": cols,
            "title": title,
            "export_url": "/home/idcard_export_zip"  # 新增导出URL参数
        })


@资料员
def idcard_export_zip(request):
    import zipfile
    from io import BytesIO

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 获取所有身份证记录
        idcards = models.IDCard.objects.all()

        for card in idcards:
            # 创建以身份证号命名的目录
            dir_name = f"{card.id_number}_{card.name}"

            # 添加人像面
            if card.front_image and card.front_image.storage.exists(card.front_image.name):
                zipf.writestr(
                    f"{dir_name}/人像面.jpg",
                    card.front_image.read()
                )

            # 添加国徽面
            if card.back_image and card.back_image.storage.exists(card.back_image.name):
                zipf.writestr(
                    f"{dir_name}/国徽面.jpg",
                    card.back_image.read()
                )

            # 添加合成图片
            if card.combined_image and card.combined_image.storage.exists(card.combined_image.name):
                zipf.writestr(
                    f"{dir_name}/合成双面.jpg",
                    card.combined_image.read()
                )

    zip_buffer.seek(0)

    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="身份证.zip"'
    return response


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


