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
from app01.services import export_service
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
from django.core.files.base import ContentFile
from app01.services.utility_service import save_image_to_field, process_photo, apply_orientation
from openpyxl import Workbook
from openpyxl.drawing.image import Image as ExcelImage
import base64
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
from django.conf import settings
import uuid
import sys
sys.path.insert(0, "/root/django")
import utils
sys.path.insert(0, "/root/django")

from django.http import HttpResponse
from datetime import datetime


from io import BytesIO

from aip import AipBodyAnalysis
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
# inventory333333333333333333333333##############################################################################################################
# inventory333333333333333333333333##############################################################################################################
# inventory333333333333333333333333##############################################################################################################

def explosivestaff_add(request):
    title = 'tu'
    if request.method == 'POST':
        if 'zip_file' in request.FILES:
            zip_file = request.FILES['zip_file']
            success_count = 0
            errors = []

            try:
                with zipfile.ZipFile(zip_file) as zf:
                    folder_files = defaultdict(dict)
                    for file_info in zf.infolist():
                        # 增强版编码修复（新增多个编码尝试）
                        raw_name = file_info.filename
                        try:
                            # 优先尝试 UTF-8 解码
                            corrected = raw_name.encode(
                                'cp437').decode('utf-8')
                        except UnicodeDecodeError:
                            try:
                                # 次尝试 GB18030 解码
                                corrected = raw_name.encode(
                                    'cp437').decode('gb18030')
                            except:
                                # 最后尝试忽略错误字符
                                corrected = raw_name.encode(
                                    'cp437').decode('utf-8', 'ignore')

                        # 跳过Mac系统文件（新增过滤）
                        if corrected.startswith('._'):
                            continue

                        if not file_info.is_dir() and '/' in corrected:
                            folder, filename = corrected.split('/', 1)
                            folder_files[folder][filename] = file_info

                    for folder, files in folder_files.items():
                        try:
                            required_files = {
                                '人像.jpg': None,
                                '国徽.jpg': None,
                                '证件照.jpg': None,
                                '无犯罪证明.jpg': None,
                                '毕业证.jpg': None
                            }

                            # 读取文件（添加调试输出）

                            for filename in required_files.keys():
                                if filename in files:
                                    try:
                                        file_info = files[filename]
                                        # 添加文件存在性验证
                                        if file_info.file_size == 0:
                                            raise ValueError(
                                                f"文件 {filename} 为空")

                                        with Image.open(io.BytesIO(zf.read(file_info))) as img:
                                            required_files[filename] = img
                                            # 添加图片有效性验证
                                            img.verify()  # 验证图片完整性
                                    except Exception as e:
                                        raise ValueError(
                                            f"文件 {filename} 损坏: {str(e)}")
                                else:
                                    raise ValueError(f"缺少文件: {filename}")

                        # 处理身份证信息

                        # 添加空值检查
                            if not all(required_files.values("name", "photo", "rotated_photo", "blue_background", "red_background", "white_background", "uploaded_at")):
                                missing = [
                                    k for k, v in required_files.items() if not v]
                                raise ValueError(f"图片加载失败: {missing}")
                                # 处理身份证信息
                                姓名, 身份证号码 = sfz(required_files['人像.jpg'])
                                print(f"姓名: {姓名}, 身份证号码: {身份证号码}")
                                # 处理各图片并保存
                                front_img = resize_photo(
                                    required_files['人像.jpg'], 3)
                                back_img = resize_photo(
                                    required_files['国徽.jpg'], 3)
                                combined_img = combine_a4_images(
                                    front_img, back_img)

                                # 保存到数据库
                                models.ExplosiveStaff.objects.create(
                                    name=姓名,
                                    id_number=身份证号码,
                                    front_image=save_image_to_field(
                                        front_img, f"{身份证号码}_front.jpg"),
                                    back_image=save_image_to_field(
                                        back_img, f"{身份证号码}_back.jpg"),
                                    combined_image=save_image_to_field(
                                        combined_img, f"{身份证号码}_combined.jpg"),
                                    photo=process_photo(
                                        required_files['证件照.jpg']),
                                    no_crime=save_image_to_field(
                                        required_files['无犯罪证明.jpg'], f"{身份证号码}_no_crime.jpg"),
                                    graduation=save_image_to_field(
                                        required_files['毕业证.jpg'], f"{身份证号码}_graduation.jpg")
                                )
                                success_count += 1

                        except Exception as e:
                            errors.append(f"{folder}: {str(e)}")

                return HttpResponse(f"成功导入 {success_count} 条记录，错误 {len(errors)} 条{errors}")

            except zipfile.BadZipFile:
                return HttpResponse("无效的ZIP文件格式", status=400)

        else:
            # 原有单个文件处理逻辑保持不变
            front_file = request.FILES.get('front')

            back_file = request.FILES.get('back')
            photo = request.FILES.get('photo')
            no_crime = request.FILES.get('no_crime')  # 原错误参数 'photo'
            graduation = request.FILES.get('graduation')  # 原错误参数 'photo'
            mobile = request.POST.get('mobile', '')  # 新增
            bank_card_number = request.POST.get('bank_card_number', '')  # 新增

            with Image.open(front_file) as img1:
                img1 = resize_photo(img1, 3)
                # 新增模式转换
                if img1.mode in ('RGBA', 'LA'):
                    img1 = img1.convert('RGB')
                img_io = io.BytesIO()
                img1.save(img_io, format='JPEG')
                img_人像 = img_io.getvalue()

            with Image.open(back_file) as img2:
                img2 = resize_photo(img2, 3)
                # 新增模式转换
                if img2.mode in ('RGBA', 'LA'):
                    img2 = img2.convert('RGB')
                img_io = io.BytesIO()
                img2.save(img_io, format='JPEG')
                img_国徽 = img_io.getvalue()

            with Image.open(photo) as img3:
                # 添加方向校正
                try:
                    exif = img3.getexif()
                    orientation = exif.get(274)  # 274是Exif方向标签
                    if orientation:
                        img3 = apply_orientation(img3, orientation)
                except Exception as e:
                    print(f"方向校正失败: {str(e)}")

                if img3.mode in ('RGBA', 'LA'):
                    img3 = img3.convert('RGB')  # 移除Alpha通道
                img_io = io.BytesIO()
                img3 = resize_photo(cut_photo(img3, 1), 1)
                img3.save(img_io, format='JPEG')
                img_bytes = img_io.getvalue()
                rotated_io = io.BytesIO()
                排版(img3, rotated_io)
                rotated_bytes = rotated_io.getvalue()

            # 处理无犯罪证明（带存在性检查）
            img_数据4 = None
            if no_crime:  # 添加文件存在判断
                with Image.open(no_crime) as img4:
                    img4 = resize_photo(img4, 4)
                    img_io = io.BytesIO()
                    img4.save(img_io, format='JPEG')
                    img_数据4 = img_io.getvalue()

            # 处理毕业证（带存在性检查）
            img_数据5 = None
            if graduation:  # 添加文件存在判断
                with Image.open(graduation) as img5:
                    img5 = resize_photo(img5, 4)
                    img_io = io.BytesIO()
                    img5.save(img_io, format='JPEG')
                    img_数据5 = img_io.getvalue()

            # 合并图片逻辑保持不变
            combined_img = combine_a4_images(img1, img2)
            img_io = io.BytesIO()
            combined_img.save(img_io, format='JPEG', quality=90)
            combined_bytes = img_io.getvalue()

            try:
                姓名, 身份证号码 = sfz(front_file)
            except:
                姓名 = "未识别"
                身份证号码 = "888888888888888888"  # 18个8

            # 修改模型引用为ExplosiveStaff
            models.ExplosiveStaff.objects.create(
                name=姓名,
                id_number=身份证号码,
                mobile=mobile,  # 新增字段
                bank_card_number=bank_card_number,
                front_image=ContentFile(img_人像, name=f"{身份证号码}_front.jpg"),
                back_image=ContentFile(img_国徽, name=f"{身份证号码}_back.jpg"),
                combined_image=ContentFile(
                    combined_bytes, name=f"{身份证号码}_combined.jpg"),

                photo=ContentFile(img_bytes, name=f"{身份证号码}_photo.jpg"),
                typeset_photo=ContentFile(
                    rotated_bytes, name=f"{身份证号码}_typeset.jpg"),
                # ... existing code ...
                no_crime=ContentFile(
                    img_数据4, name=f"{身份证号码}_no_crime.jpg") if img_数据4 else None,
                graduation=ContentFile(
                    img_数据5, name=f"{身份证号码}_graduation.jpg") if img_数据5 else None,
                # ... existing code ...

            )

            return HttpResponse("""
                <div style="
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                ">
                    <h1 style="font-size: 48px; margin: 0">数据上传成功</h1>
                </div>
            """)

    else:
        model_names = models.ExplosiveStaff.objects.values_list(
            'id_number', flat=True).distinct()
        return render(request, 'explosivestaff_add.html', {
            'model_names': model_names,
            'zip_upload': True
        })


def explosivestaff_delete(request):
    id = request.GET.get('id')
    models.ExplosiveStaff.objects.filter(id=str(id)).delete()
    return redirect("/home/explosivestaff_list")  # 修改重定向路径


def explosivestaff_list(request):
    title = 'explosivestaff'
    if request.method == "GET":
        model_fields = models.ExplosiveStaff._meta.fields
        cols = [{'verbose_name': field.verbose_name} for field in model_fields if field.attname not in ('id', 'location')]
        cols.append({'verbose_name': '操作'})
        data = models.ExplosiveStaff.objects.values("name", "photo", "rotated_photo", "blue_background", "red_background", "white_background", "uploaded_at").order_by(
            '-created_at')[:100]
        return render(request, 'explosivestaff_list.html', {
            "data": data,
            "cols": cols,
            "title": title,
            "export_url": "/home/explosivestaff_export_zip",
            "export_xlsx_url": "/home/explosivestaff_export_xlsx"  # 新增XLSX导出参数
        })
# 新增Excel导出函数


def explosivestaff_export_xlsx(request):
    from datetime import datetime

    excel_io = export_service.explosivestaff_export_xlsx()
    response = HttpResponse(
        excel_io.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"explosivestaff_{datetime.now().strftime('%Y%m%d%H%M')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
# 新增的导出函数


def explosivestaff_export_zip(request):
    zip_buffer = export_service.explosivestaff_export_zip()
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="explosivestaff_images.zip"'
    return response


