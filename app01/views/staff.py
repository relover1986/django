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


class StaffListView(FilterView, ListView):
    model = models.Admin
    template_name = 'staff_list.html'
    context_object_name = 'data'
    filterset_class = modelform.StaffFilter
    paginate_by = 100  # 每页显示的记录数
    ordering = ['id']  # 默认排序字段

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '员工列表'
        context['cols'] = [
            {'col_name': 'ID'},
            {'col_name': '标识'},
            {'col_name': '用户名'},
            {'col_name': '身份'},
            {'col_name': '部门'},
            {'col_name': '操作'},
        ]
        return context


def staff_list(request):
    title = '管理员'

    if request.method == "GET":

        # 将 QuerySet 转换为 DataFrame
        df = pd.DataFrame.from_records(
            models.Admin.objects.exclude(role='学前班同学').values("name", "photo", "rotated_photo", "blue_background", "red_background", "white_background", "uploaded_at")
        )

        # 根据 ident 列去重，保留最后一行
        df = df.drop_duplicates(subset='ident', keep='last')

        df = df.sort_values(by='ident', ascending=False)

        # 将 DataFrame 转换回列表
        data = df.to_dict('records')

        lst = dframe(data)

        cols = []
        for i in lst:
            cols.append({'col_name': i})

        return render(request, 'staff_list.html', {"data": data, "cols": cols, "title": title})

    return render(request, 'staff_list.html', {"title": title})


@资料员
def admin_add(request):

    title = '新建员工信息'
    if request.method == "GET":
        form = modelform.Staff()
        return render(request, 'create.html', {"form": form, "标题": title})
    print("request.FILES:", request.FILES)
    form = modelform.Staff(data=request.POST, files=request.FILES)

    if form.is_valid():
        form.save()
        print("清洗后数据:", form.cleaned_data)  # 注意：is_valid()=False时可能不完整
        print("错误信息:", form.errors.as_json())

    else:
        # 打印原始提交数据
        print("原始提交数据:", form.data)

        # 打印每个字段的值
        for field in form:
            print(f"字段 [{field.name}] 值: {field.data} | 错误: {field.errors}")

        # 或者更直接的调试方式
        print("清洗后数据:", form.cleaned_data)  # 注意：is_valid()=False时可能不完整
        print("错误信息:", form.errors.as_json())

        title = '输入错误'

        return render(request, 'create.html', {"form": form, "标题": title})

    return redirect("/home/admin")


@最高权限
def admin_delete(request):

    id = request.GET.get('id')
    models.Admin.objects.filter(id=str(id)).delete()
    return redirect("/home/admin")


@最高权限
def admin_edit(request):
    id = request.GET.get('id')
    row_object = models.Admin.objects.filter(id=str(id)).first()
    title = f'员工信息编辑 - {row_object.username}' if row_object else '员工信息编辑'
    if request.method == "GET":

        form = modelform.Staff(instance=row_object)

        return render(request, 'change.html', {"form": form, "title": title})

    form = modelform.Staff(
        instance=row_object,  # 先指定要编辑的实例
        data=request.POST,     # 后传入提交数据
        files=request.FILES    # 最后传入文件
    )

    if form.is_valid():

        form.save()
    else:
        title = '输入错误'
        form.errors
        return render(request, 'change.html', {"form": form, "title": title})
    return redirect("/home/admin")


#     ⌘ + K → ⌘ + J       # macOS ⌘ + Shift + ]


# ========== idcard_batch_upload ==========
from functools import wraps
from django.shortcuts import get_object_or_404
from app01.forms import StaffForm, CertTypeForm, StaffCertForm
from app01.models import Staff, CertType, StaffCert


from app01.permissions import login_required


@login_required
def staff_list(request):
    """人员列表"""
    data = Staff.objects.all().order_by("-created_at")
    paginator = Paginator(data, 20)
    page_number = request.GET.get("page", 1)
    try:
        page_obj = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)
    return render(request, "staff_list_new.html", {
        "data": page_obj,
        "title": "人员管理",
        "is_paginated": True,
        "paginator": paginator,
        "page_obj": page_obj,
    })


@login_required
def staff_add(request):
    """新增人员"""
    if request.method == "GET":
        form = StaffForm()
        return render(request, "staff_form.html", {"form": form, "title": "新增人员"})
    form = StaffForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect("/home/admin/")
    return render(request, "staff_form.html", {"form": form, "title": "新增人员"})


@login_required
def staff_edit_v2(request, pk):
    """编辑人员"""
    obj = get_object_or_404(Staff, pk=pk)
    if request.method == "GET":
        form = StaffForm(instance=obj)
        return render(request, "staff_form.html", {"form": form, "title": "编辑人员", "obj": obj})
    form = StaffForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("/home/admin/")
    return render(request, "staff_form.html", {"form": form, "title": "编辑人员", "obj": obj})


@login_required
def staff_detail(request, pk):
    """人员详情（含证件列表）"""
    obj = get_object_or_404(Staff, pk=pk)
    certs = obj.staffcert_set.all().order_by("-created_at")
    # 为每个证件预取附件
    for cert in certs:
        cert.files = cert.staffcertfile_set.all()
    return render(request, "staff_detail.html", {
        "obj": obj,
        "certs": certs,
        "title": f"{obj.name} - 详情",
    })


@login_required
def staff_delete_v2(request, pk):
    """删除人员"""
    obj = get_object_or_404(Staff, pk=pk)
    obj.delete()
    return redirect("/home/admin/")


@login_required
def staff_cert_add(request, pk):
    """为人员添加证件"""
    staff_obj = get_object_or_404(Staff, pk=pk)
    if request.method == "GET":
        form = StaffCertForm(initial={"staff": staff_obj.pk})
        return render(request, "staff_cert_form.html", {
            "form": form, "staff_obj": staff_obj,
            "title": f"{staff_obj.name} - 添加证件",
        })
    form = StaffCertForm(request.POST)
    if form.is_valid():
        cert = form.save(commit=False)
        cert.staff = staff_obj
        cert.save()
        return redirect("/staff/{}/".format(pk))
    return render(request, "staff_cert_form.html", {
        "form": form, "staff_obj": staff_obj,
        "title": f"{staff_obj.name} - 添加证件",
    })


@login_required
def staff_cert_delete(request, pk):
    """删除证件"""
    cert = get_object_or_404(StaffCert, pk=pk)
    staff_pk = cert.staff.pk
    cert.delete()
    return redirect("/staff/{}/".format(staff_pk))


# ---------- 证件类型管理 ----------

@login_required
def cert_type_list(request):
    """证件类型列表"""
    data = CertType.objects.all().order_by("sort", "id")
    return render(request, "cert_type_list.html", {
        "data": data,
        "title": "证件类型管理",
    })


@login_required
def cert_type_add(request):
    """新增证件类型"""
    if request.method == "GET":
        form = CertTypeForm()
        return render(request, "cert_type_form.html", {"form": form, "title": "新增证件类型"})
    form = CertTypeForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect("/cert-type/")
    return render(request, "cert_type_form.html", {"form": form, "title": "新增证件类型"})


@login_required
def cert_type_edit(request, pk):
    """编辑证件类型"""
    obj = get_object_or_404(CertType, pk=pk)
    if request.method == "GET":
        form = CertTypeForm(instance=obj)
        return render(request, "cert_type_form.html", {"form": form, "title": "编辑证件类型", "obj": obj})
    form = CertTypeForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("/cert-type/")
    return render(request, "cert_type_form.html", {"form": form, "title": "编辑证件类型", "obj": obj})


@login_required
def cert_type_delete(request, pk):
    """删除证件类型"""
    obj = get_object_or_404(CertType, pk=pk)
    obj.delete()
    return redirect("/cert-type/")


# ============================================================
# 入井证 — mine_card
# ============================================================
