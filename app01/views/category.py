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
# categorycontent------------------------------------------------------------------------------------------------------------------------------
# categorycontent------------------------------------------------------------------------------------------------------------------------------
# categorycontent------------------------------------------------------------------------------------------------------------------------------
# categorycontent------------------------------------------------------------------------------------------------------------------------------


def categorycontent_list(request):

    database = 'categorycontent'
    title = '民爆物品'
    if request.method == "GET":

        data = models.CategoryContent.objects.values("name", "photo", "rotated_photo", "blue_background", "red_background", "white_background", "uploaded_at")[:100]

        lst = dframe(data)
        cols = []

        for i in lst:
            cols.append({'age': i})

        return render(request, 'list.html', {"data": data, "cols": cols, "数据库": database, '标题': title})


def categorycontent_create(request):
    title = '民爆物品'

    if request.method == "GET":

        form = modelform.CategoryContentForm()

        return render(request, 'card_form.html', {'form': form, '标题': title})

    if request.method == 'POST':
        form = modelform. CategoryContentForm(request.POST)

        if form.is_valid():
            form.save()

        else:
            form.errors
            return render(request, 'card_form.html', {'form': form, '标题': title})

    return redirect("/home/categorycontent_list")


def categorycontent_delete(request):

    id = request.GET.get('id')
    models.CategoryContent.objects.filter(id=str(id)).delete()
    return redirect("/home/categorycontent_list")


def categorycontent_edit(request):
    title = '民爆物品'
    id = request.GET.get('id')
    row_object = models.CategoryContent.objects.filter(id=str(id)).first()

    if request.method == "GET":

        form = modelform.CategoryContentForm(instance=row_object)

        return render(request, 'card_form.html', {"form": form, "标题": title})

    form = modelform.CategoryContentForm(
        data=request.POST, instance=row_object)

    if form.is_valid():

        form.save()
    else:
        title = '输入错误'
        form.errors
        return render(request, 'card_form.html', {'form': form})
    return redirect("/home/categorycontent_list")


