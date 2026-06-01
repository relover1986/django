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



# photo++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@csrf_exempt
@api_view(['POST'])
def api_photo_add(request):
    if request.method != 'POST':
        return Response({'error': 'Only POST requests are allowed'}, status=405)
    
    try:
        from app01.serializers import PhotoUploadSerializer
        # 使用序列化器验证请求数据
        serializer = PhotoUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Validation failed',
                'details': serializer.errors
            }, status=400)
        
        # 获取上传的文件
        file = serializer.validated_data.get('file')
        model_name = serializer.validated_data.get('model_name', '')
        
        if not file:
            return Response({'error': 'No files uploaded'}, status=400)
        
        # 处理上传的照片
        filename = model_name[:10] if model_name else os.path.splitext(file.name)[0][:10]

        img = Image.open(file)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')

        img = resize_photo(cut_photo(img, 1), 1)
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG', quality=45, optimize=True, subsampling='4:2:0')
        img_bytes = img_io.getvalue()

        result = client.bodySeg(img_bytes)

        if 'foreground' in result:
            # 转换前景图
            foreground = Image.open(io.BytesIO(
                base64.b64decode(result['foreground'])))

            # 一寸照片标准尺寸
            output_size = (295, 413)
            foreground.thumbnail(output_size)

            # 创建三种背景色
            background_colors = {
                '蓝底': (67, 142, 219),
                '红底': (255, 0, 0),
                '白底': (255, 255, 255)
            }

            # 存储排版后的背景图
            bg_files = {
                'blue': None,
                'red': None,
                'white': None
            }

            # 生成并排版所有背景图
            for name, color in background_colors.items():
                # 生成背景
                background = Image.new('RGB', output_size, color)
                x = (output_size[0] - foreground.width) // 2
                y = (output_size[1] - foreground.height) // 2
                background.paste(foreground, (x, y), foreground)

                # 对背景图进行排版
                rotated_bg_io = io.BytesIO()
                排版(background, rotated_bg_io)
                rotated_bg_bytes = rotated_bg_io.getvalue()

                # 根据背景类型存储
                if name == '蓝底':
                    bg_files['blue'] = ContentFile(
                        rotated_bg_bytes, name=f"{filename}_blue.jpg")
                elif name == '红底':
                    bg_files['red'] = ContentFile(
                        rotated_bg_bytes, name=f"{filename}_red.jpg")
                elif name == '白底':
                    bg_files['white'] = ContentFile(
                        rotated_bg_bytes, name=f"{filename}_white.jpg")

            # 对原始图进行排版
            rotated_io = io.BytesIO()
            排版(img, rotated_io)
            rotated_bytes = rotated_io.getvalue()

            # 创建模型实例并保存所有图片
            uploaded_photo = UploadedZhaopian.objects.create(
                name=filename,
                photo=ContentFile(img_bytes, name=f"{filename}.jpg"),
                rotated_photo=ContentFile(
                    rotated_bytes, name=f"{filename}_rotated.jpg"),
                blue_background=bg_files['blue'],
                red_background=bg_files['red'],
                white_background=bg_files['white']
            )

            # 构建照片URL
            photo_data = {
                'id': uploaded_photo.id,
                'name': uploaded_photo.name,
                'photo': uploaded_photo.photo.url if uploaded_photo.photo else '',
                'rotated_photo': uploaded_photo.rotated_photo.url if uploaded_photo.rotated_photo else '',
                'blue_background': uploaded_photo.blue_background.url if uploaded_photo.blue_background else '',
                'red_background': uploaded_photo.red_background.url if uploaded_photo.red_background else '',
                'white_background': uploaded_photo.white_background.url if uploaded_photo.white_background else ''
            }
        else:
            return Response({'error': 'Failed to segment image foreground'}, status=500)

        return Response({
            'code': 200,
            'message': 'Photo uploaded successfully',
            'result': photo_data
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


# API 视图类
class PhotoListAPIView(APIView):
    def get(self, request, format=None):
        try:
            from app01.serializers import UploadedZhaopianSerializer
            photos = UploadedZhaopian.objects.all().order_by('-uploaded_at')
            serializer = UploadedZhaopianSerializer(photos, many=True)
            return Response({
                'code': 200,
                'message': 'Photos retrieved successfully',
                'results': serializer.data,
                'count': photos.count()
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PhotoDetailAPIView(APIView):
    def get(self, request, photo_id, format=None):
        try:
            from app01.serializers import UploadedZhaopianSerializer
            photo = UploadedZhaopian.objects.get(id=photo_id)
            serializer = UploadedZhaopianSerializer(photo)
            return Response({
                'code': 200,
                'message': 'Photo retrieved successfully',
                'result': serializer.data
            }, status=status.HTTP_200_OK)
        except models.UploadedZhaopian.DoesNotExist:
            return Response({'error': 'Photo not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PhotoDeleteAPIView(APIView):
    def delete(self, request, photo_id, format=None):
        try:
            photo = models.UploadedZhaopian.objects.get(id=photo_id)
            photo.delete()
            return Response({
                'code': 200,
                'message': 'Photo deleted successfully'
            }, status=status.HTTP_200_OK)
        except models.UploadedZhaopian.DoesNotExist:
            return Response({'error': 'Photo not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PhotoUploadAPIView(APIView):
    def post(self, request, format=None):
        files = request.FILES.getlist('file')
        results = []
        
        if not files:
            return Response({'error': 'No files provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        for file in files:
            time.sleep(0.1)
            try:
                # 人脸对齐：先保存到临时文件，对齐后替换原图
                import tempfile as _tf
                _tmp = _tf.NamedTemporaryFile(suffix='.jpg', delete=False)
                for chunk in file.chunks():
                    _tmp.write(chunk)
                _tmp_path = _tmp.name
                _tmp.close()
                try:
                    img = Image.open(_tmp_path).convert('RGB')
                finally:
                    os.unlink(_tmp_path)

                if img.mode in ('RGBA', 'LA'):
                    img = img.convert('RGB')  # 移除Alpha通道

                # 获取文件名
                if len(files) == 1 and 'model_name' in request.data:
                    filename = request.data['model_name'][:10]
                    if len(filename) == 0:
                        filename = os.path.splitext(file.name)[0][:10]
                else:
                    filename = os.path.splitext(file.name)[0][:10]

                # 处理图片
                img_io = io.BytesIO()
                img = resize_photo(cut_photo(img, 1), 1)  # 使用您现有的函数
                img.save(img_io, format='JPEG')
                img_bytes = img_io.getvalue()

                # 人体分割
                result = client.bodySeg(img_bytes)  # 使用您现有的client

                if 'foreground' in result:
                    # 处理前景图
                    foreground = Image.open(io.BytesIO(
                        base64.b64decode(result['foreground'])))

                    # 一寸照片标准尺寸
                    output_size = (295, 413)
                    foreground.thumbnail(output_size)

                    # 创建三种背景色
                    background_colors = {
                        '蓝底': (67, 142, 219),
                        '红底': (255, 0, 0),
                        '白底': (255, 255, 255)
                    }

                    # 存储排版后的背景图
                    bg_files = {
                        'blue': None,
                        'red': None,
                        'white': None
                    }

                    # 生成并排版所有背景图
                    for name, color in background_colors.items():
                        background = Image.new('RGB', output_size, color)
                        x = (output_size[0] - foreground.width) // 2
                        y = (output_size[1] - foreground.height) // 2
                        background.paste(foreground, (x, y), foreground)

                        rotated_bg_io = io.BytesIO()
                        排版(background, rotated_bg_io)  # 使用您现有的函数
                        rotated_bg_bytes = rotated_bg_io.getvalue()

                        if name == '蓝底':
                            bg_files['blue'] = ContentFile(
                                rotated_bg_bytes, name=f"{filename}_blue.jpg")
                        elif name == '红底':
                            bg_files['red'] = ContentFile(
                                rotated_bg_bytes, name=f"{filename}_red.jpg")
                        elif name == '白底':
                            bg_files['white'] = ContentFile(
                                rotated_bg_bytes, name=f"{filename}_white.jpg")

                    # 对原始图进行排版
                    rotated_io = io.BytesIO()
                    排版(img, rotated_io)  # 使用您现有的函数
                    rotated_bytes = rotated_io.getvalue()

                    # 创建模型实例
                    uploaded_photo = UploadedZhaopian.objects.create(
                        name=filename,
                        photo=ContentFile(img_bytes, name=f"{filename}.jpg"),
                        rotated_photo=ContentFile(
                            rotated_bytes, name=f"{filename}_rotated.jpg"),
                        blue_background=bg_files['blue'],
                        red_background=bg_files['red'],
                        white_background=bg_files['white']
                    )

                    # 序列化返回数据
                    serializer = UploadedZhaopianSerializer(uploaded_photo)
                    results.append(serializer.data)

            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
    'code': 200,
    'results': results,
    'photo_urls': [
        {
            'name': item['name'],
            'original': item['photo'],
            'rotated': item['rotated_photo'],
            'blue': item['blue_background'],
            'red': item['red_background'],
            'white': item['white_background']
        } for item in results
    ]
}, status=status.HTTP_200_OK)







def photo_add(request):
    title = 'tu'
    if request.method == 'POST':
        # 删除原来的 model_name 获取逻辑
        files = request.FILES.getlist('file')
        if len(files) > 10:
            return render(request, 'photo_add.html', {'model_names': [], 'error': '最多上传10张照片'})

        import traceback as _tb
        success = 0
        failed = 0

        for file in files:
            time.sleep(0.1)
            try:
                # 人脸对齐：先保存到临时文件，对齐后替换原图
                import tempfile as _tf
                _tmp = _tf.NamedTemporaryFile(suffix='.jpg', delete=False)
                for chunk in file.chunks():
                    _tmp.write(chunk)
                _tmp_path = _tmp.name
                _tmp.close()
                try:
                    img = Image.open(_tmp_path).convert('RGB')
                finally:
                    os.unlink(_tmp_path)

                if img.mode in ('RGBA', 'LA'):
                    img = img.convert('RGB')  # 移除Alpha通道

                if len(files) == 1:
                    filename = request.POST['model_name'][:10]
                    if len(filename) == 0:
                        filename = os.path.splitext(file.name)[0][:10]
                else:
                    filename = os.path.splitext(file.name)[0][:10]

                img_io = io.BytesIO()
                img = resize_photo(cut_photo(img, 1), 1)
                img.save(img_io, format='JPEG')
                img_bytes = img_io.getvalue()

                result = client.bodySeg(img_bytes)
                has_foreground = 'foreground' in result

                if has_foreground:
                    foreground = Image.open(io.BytesIO(
                        base64.b64decode(result['foreground'])))
                    output_size = (295, 413)
                    foreground.thumbnail(output_size)

                    background_colors = {
                        '蓝底': (67, 142, 219),
                        '红底': (255, 0, 0),
                        '白底': (255, 255, 255)
                    }
                    bg_files = {'blue': None, 'red': None, 'white': None}
                    white_bg_single_file = None

                    for name, color in background_colors.items():
                        background = Image.new('RGB', output_size, color)
                        x = (output_size[0] - foreground.width) // 2
                        y = (output_size[1] - foreground.height) // 2
                        background.paste(foreground, (x, y), foreground)

                        if name == '白底':
                            single_io = io.BytesIO()
                            background.save(single_io, format='JPEG')
                            white_bg_single_file = ContentFile(
                                single_io.getvalue(), name=f"{filename}_white_single.jpg")

                        rotated_bg_io = io.BytesIO()
                        排版(background, rotated_bg_io)
                        rotated_bg_bytes = rotated_bg_io.getvalue()

                        if name == '蓝底':
                            bg_files['blue'] = ContentFile(rotated_bg_bytes, name=f"{filename}_blue.jpg")
                        elif name == '红底':
                            bg_files['red'] = ContentFile(rotated_bg_bytes, name=f"{filename}_red.jpg")
                        elif name == '白底':
                            bg_files['white'] = ContentFile(rotated_bg_bytes, name=f"{filename}_white.jpg")

                    rotated_io = io.BytesIO()
                    排版(img, rotated_io)
                    rotated_bytes = rotated_io.getvalue()

                    models.UploadedZhaopian.objects.create(
                        name=filename,
                        photo=ContentFile(img_bytes, name=f"{filename}.jpg"),
                        rotated_photo=ContentFile(rotated_bytes, name=f"{filename}_rotated.jpg"),
                        blue_background=bg_files['blue'],
                        red_background=bg_files['red'],
                        white_background=bg_files['white'],
                        white_bg_single=white_bg_single_file
                    )
                else:
                    # bodySeg 失败，至少保存原始照片
                    rotated_io = io.BytesIO()
                    排版(img, rotated_io)
                    rotated_bytes = rotated_io.getvalue()
                    models.UploadedZhaopian.objects.create(
                        name=filename,
                        photo=ContentFile(img_bytes, name=f"{filename}.jpg"),
                        rotated_photo=ContentFile(rotated_bytes, name=f"{filename}_rotated.jpg"),
                    )
                success += 1
            except Exception as _e:
                failed += 1
                print(f"[photo_add] 处理失败 {file.name}: {_e}")
                _tb.print_exc()

        msg = f"上传完成：成功 {success} 张"
        if failed:
            msg += f"，{failed} 张处理失败（已跳过）"
        return redirect(f"/home/photo_list?msg={msg}")

    else:
        model_names = models.UploadedZhaopian.objects.values_list(
            'name', flat=True).distinct()
        return render(request, 'photo_add.html', {'model_names': model_names})


def photo_delete(request):
    id = request.GET.get('id')
    models.UploadedZhaopian.objects.filter(id=str(id)).delete()
    return redirect("/home/photo_list")


@csrf_exempt
def photo_batch_delete(request):
    if request.method == 'POST':
        ids = request.POST.get('ids', '')
        if ids:
            id_list = [i.strip() for i in ids.split(',') if i.strip()]
            deleted, _ = models.UploadedZhaopian.objects.filter(id__in=id_list).delete()
            return JsonResponse({'code': 200, 'deleted': deleted})
    return JsonResponse({'error': 'invalid request'}, status=400)


def photo_list(request):
    title = 'photo'
    if request.method == "GET":
        model_fields = models.UploadedZhaopian._meta.fields
        cols = [{'verbose_name': field.verbose_name} for field in model_fields if field.attname not in ('id', 'location', 'photo', 'rotated_photo')]
        cols.append({'verbose_name': '操作'})
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
        queryset = models.UploadedZhaopian.objects.values("id", "name", "blue_background", "red_background", "white_background", "white_bg_single", "uploaded_at").order_by('-uploaded_at')
        paginator = Paginator(queryset, 20)
        page = request.GET.get('page', 1)
        try:
            data = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            data = paginator.page(1)
        return render(request, 'photo_list.html', {
            "data": data,
            "cols": cols,
            "title": title,
            "export_url": "/home/photo_export_zip",
        })


@csrf_exempt
@api_view(["POST"])
def generate_white_bg(request):
    """生成白底一寸照（不排版），存入 white_bg_single 字段"""
    try:
        photo_id = request.data.get("photo_id")
        photo = UploadedZhaopian.objects.get(id=photo_id)

        img = Image.open(photo.photo.path).convert('RGB')
        img = resize_photo(cut_photo(img, 1), 1)

        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_bytes = img_io.getvalue()

        result = client.bodySeg(img_bytes)

        if 'foreground' not in result:
            return JsonResponse({"code": 500, "error": "bodySeg failed: no foreground"})

        foreground = Image.open(io.BytesIO(base64.b64decode(result['foreground'])))
        output_size = (295, 413)
        foreground.thumbnail(output_size)

        background = Image.new("RGB", output_size, (255, 255, 255))
        x = (output_size[0] - foreground.width) // 2
        y = (output_size[1] - foreground.height) // 2
        background.paste(foreground, (x, y), foreground)

        # 不排版，直接保存单张白底一寸照
        single_io = io.BytesIO()
        background.save(single_io, format='JPEG')
        single_bytes = single_io.getvalue()

        photo.white_bg_single.save(
            f"{photo.id}_white_single.jpg",
            ContentFile(single_bytes)
        )
        photo.save()

        return JsonResponse({"code": 200, "url": photo.white_bg_single.url})

    except Exception as e:
        return JsonResponse({"code": 500, "error": str(e)})


@资料员
def photo_export_zip(request):
    import zipfile
    from io import BytesIO

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        photos = models.UploadedZhaopian.objects.all()

        for photo in photos:
            # 使用ID作为唯一标识符防止重名
            prefix = f"{photo.id}_{photo.name}" if photo.name else str(
                photo.id)

            # 原始照片
            if photo.photo and photo.photo.storage.exists(photo.photo.name):
                zipf.writestr(
                    f"{prefix}_原始照片.jpg",  # 直接根目录
                    photo.photo.read()
                )

            # 三种背景照片
            background_fields = [
                ('blue_background', '蓝底'),
                ('red_background', '红底'),
                ('white_background', '白底')
            ]

            for field, name in background_fields:
                img_field = getattr(photo, field)
                if img_field and img_field.storage.exists(img_field.name):
                    zipf.writestr(
                        f"{prefix}_{name}照片.jpg",  # 直接根目录
                        img_field.read()
                    )

    zip_buffer.seek(0)

    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="寸照.zip"'
    return response

# ++++爆破++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++爆破++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++爆破++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


