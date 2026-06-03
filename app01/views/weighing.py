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
# weighingrecords333333333333333333333333#weighingrecords333333333333333333333333#weighingrecords333333333333333333333333
# weighingrecords333333333333333333333333#weighingrecords333333333333333333333333#weighingrecords333333333333333333333333
# weighingrecords333333333333333333333333#weighingrecords333333333333333333333333#weighingrecords333333333333333333333333
# weighingrecords333333333333333333333333#weighingrecords333333333333333333333333#weighingrecords333333333333333333333333


def weighingrecord_add(request):
    title = 'weighingrecord'
    if request.method == "GET":

        form = modelform.WeighingRecordForm()

        return render(request, 'card_form.html', {'form': form, '标题': title})

    if request.method == 'POST':
        form = modelform.WeighingRecordForm(
            request.POST, request.FILES)  # <-- 添加request.FILES

        if form.is_valid():

            form.save()

        else:

            form.errors
            return render(request, 'card_form.html', {'form': form, '标题': title})

    return redirect("/home/weighingrecord_list")


@require_role("爆破工程技术人员", "资料员")
def weighingrecord_delete(request):
    id = request.GET.get('id')
    models.WeighingRecord.objects.filter(id=str(id)).delete()
    return redirect("/home/weighingrecord_list")


def weighingrecord_list(request):
    title = 'weighingrecord'
    if request.method == "GET":
        data = models.WeighingRecord.objects.values("name", "photo", "rotated_photo", "blue_background", "red_background", "white_background", "uploaded_at").order_by(
            'weight_number', '-created_at')
        # 获取模型字段的verbose_name
        model_fields = models.WeighingRecord._meta.fields
        cols = [{'verbose_name': 'id'}] + [{'verbose_name': field.verbose_name}
                                           for field in model_fields if field.name != 'id']

        # 添加操作列
        cols.append({'verbose_name': '操作'})

        return render(request, 'weighingrecord_list.html', {
            "data": data,
            "cols": cols,
            "title": title
        })


