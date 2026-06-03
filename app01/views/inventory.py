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
# inventory333333333333333333333333##############################################################################################################


def inventory_list(request):

    title = 'inventory'
    database = '出入库记录'

    if request.method == "GET":

        model_fields = models.ExplosiveInventoryItem._meta.fields
        cols = [{'verbose_name': field.verbose_name} for field in model_fields if field.attname not in ('id', 'location')]
        cols.append({'verbose_name': '操作'})
        data = models.ExplosiveInventoryItem.objects.values("name", "photo", "rotated_photo", "blue_background", "red_background", "white_background", "uploaded_at").order_by(
            '-date')[:100]

        return render(request, 'inventory_list.html', {"data": data, "cols": cols, "数据库": database, 'title': title, "export_xlsx_url": "/home/inventory_export_xlsx"  # 新增XLSX导出参数
                                                       })


def inventory_add(request):
    title = '出入库记录'

    if request.method == "GET":

        form = ExplosiveInventoryItemForm()

        return render(request, 'card_form.html', {'form': form, '标题': title})

    if request.method == 'POST':
        form = ExplosiveInventoryItemForm(request.POST)

        if form.is_valid():

            form.save()

        else:

            form.errors
            return render(request, 'card_form.html', {'form': form, '标题': title})

    return redirect("/home/inventory_list")


def inventory_delete(request):

    id = request.GET.get('id')
    models.ExplosiveInventoryItem.objects.filter(id=str(id)).delete()
    return redirect("/home/inventory_list")


def inventory_edit(request):

    title = '出入库记录'
    id = request.GET.get('id')
    row_object = models.ExplosiveInventoryItem.objects.filter(
        id=str(id)).first()

    if request.method == "GET":

        form = modelform.ExplosiveInventoryItemForm(instance=row_object)

        return render(request, 'card_form.html', {"form": form, "标题": title})

    form = modelform.ExplosiveInventoryItemForm(
        data=request.POST, instance=row_object)

    if form.is_valid():

        form.save()
    else:
        title = '输入错误'
        form.errors
        return render(request, 'card_form.html', {'form': form})
    return redirect("/home/inventory_list")


def inventory_export_xlsx(request):
    from datetime import datetime

    excel_io = export_service.inventory_export_xlsx()
    response = HttpResponse(
        excel_io.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"inventory_{datetime.now().strftime('%Y%m%d%H%M')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


