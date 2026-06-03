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
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


def pdf_add(request):
    title = 'tu'
    if request.method == 'POST':

        model_name = request.POST['model_name']
        files = request.FILES.getlist('file')  # 获取所有上传的文件

        for file in files:
            time.sleep(0.1)
            # 处理每个文件，例如保存到数据库或文件系统
            models.UploadedPDF.objects.create(
                model_name=model_name, pdf_file=file)

        return redirect("/home/pdf_list")

    else:
        model_names = models.UploadedPDF.objects.values_list(
            'model_name', flat=True).distinct()
        return render(request, 'pdf_add.html', {'model_names': model_names})


def pdf_delete(request):

    id = request.GET.get('id')
    models.UploadedPDF.objects.filter(id=str(id)).delete()
    return redirect("/home/pdf_list")


def pdf_list(request):

    title = 'pdf'
    if request.method == "GET":

        data = models.UploadedPDF.objects.values("id", "model_name", "pdf_file")[:100]

        # print(data)

        lst = dframe(data)
        cols = []

        for i in lst:
            cols.append({'age': i})

        return render(request, 'pdf_list.html', {"data": data, "cols": cols, "title": title})


