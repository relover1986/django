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
# ---------------------------------------------------------------------------------------


def upload_model(request):
    # 获取指定应用中的所有模型
    app_models = apps.get_app_config('app01').get_models()
    model_names = [model.__name__ for model in app_models]

    if request.method == 'POST':
        model_name = request.POST.get('model_name')
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            # 处理上传的 '.xlsx' 文件
            df = pd.read_excel(uploaded_file)
            df['password'] = df['password'].apply(lambda x: md5(str(x)))
            # 这里可以根据选择的模型表名进行相应的处理
            print(f"选择的模型表: {model_name}")
            print(df.head())
            try:
                with sl.connect('/Users/sunhongchen/lnjx2025/db.sqlite3') as con:
                    df.to_sql(f'app01_{model_name.lower()}',
                              con, index=False, if_exists='append')

                return HttpResponse("文件上传成功！")
            except Exception as e:
                return HttpResponse(f"文件上传失败: {str(e)}")

    return render(request, 'upload.html', {'model_names': model_names})


