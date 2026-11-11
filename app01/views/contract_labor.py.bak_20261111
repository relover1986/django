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
from app01.services import export_service
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


def contractlabor_add(request):
    title = 'tu'
    if request.method == 'POST':
        # 删除原来的 model_name 获取逻辑
        files = request.FILES.getlist('file')
        for file in files:
            time.sleep(0.1)
            if file.name.endswith('.xlsx'):
                wb = load_workbook(file)
            elif file.name.endswith('.docx'):
                document = Document(file)

        ws = wb.worksheets[0]
        row_No = ws.max_row+1
        col_No = ws.max_column+1
        for table_row in range(2, row_No):
            for file in files:
                if file.name.endswith('.xlsx'):
                    wb = load_workbook(file)
                elif file.name.endswith('.docx'):
                    document = Document(file)

            for table_col in range(1, col_No):
                合同(str(ws.cell(1, table_col).value), str(
                    ws.cell(table_row, table_col).value), document)

            姓名 = str(ws.cell(table_row, 3).value)
            img_io = io.BytesIO()

            document.save(img_io)
            document_bytes = img_io.getvalue()  # 直接获取字节数据

            # 创建模型实例
            models.ContractLabor.objects.create(
                name=str(ws.cell(table_row, 3).value),
                id_number=str(ws.cell(table_row, 7).value),
                contract_file=ContentFile(document_bytes, name=f"{姓名}.docx"),

            )

        return redirect("/home/contractlabor_list")

    else:
        model_names = models.ContractLabor.objects.values_list(
            'name', flat=True).distinct()
        return render(request, 'contractlabor_add.html', {'model_names': model_names})


def contractlabor_delete(request):

    id = request.GET.get('id')
    models.ContractLabor.objects.filter(id=str(id)).delete()
    return redirect("/home/contractlabor_list")


def contractlabor_list(request):
    title = 'contractlabor'
    if request.method == "GET":
        data = models.ContractLabor.objects.values("name", "id_number", "contract_file", "created_at").order_by('-id')[:100]
        model_fields = models.ContractLabor._meta.fields
        cols = [{'verbose_name': field.verbose_name} for field in model_fields if field.attname not in ('id', 'location')]

        # 添加操作列
        cols.append({'verbose_name': '操作'})
        return render(request, 'contractlabor_list.html', {
            "data": data,
            "cols": cols,
            "title": title,
            "export_url": "/home/contractlabor_export_zip"  # 新增导出参数
        })

# 新增合同导出函数


@require_role("爆破工程技术人员", "资料员")
def contractlabor_export_zip(request):
    zip_buffer = export_service.contractlabor_export_zip()
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="labor_contracts.zip"'
    return response



def design_list(request):
    """设计批量处理 — 独立列表（不与合同共用）"""
    data = models.DesignDoc.objects.order_by('-id')[:200]
    return render(request, 'design_list.html', {'data': data})


def design_upload(request):
    """设计批量处理 — 上传：按行出，每行 x 每个模板各一份"""
    import re as _re
    if request.method == 'POST':
        files = request.FILES.getlist('file')
        xlsxs = [f for f in files if f.name.lower().endswith('.xlsx')]
        tpls = [f for f in files if f.name.lower().endswith('.docx')]
        if not xlsxs or not tpls:
            return render(request, 'kztqhp.html',
                          {'error': '请同时上传 1 个 Excel(.xlsx) 和至少 1 个 Word 模板(.docx)'})
        wb = load_workbook(xlsxs[0])
        ws = wb.worksheets[0]
        # 编号列：表头含「编号」优先，否则第3列（合同姓名位；实测该列即 45m3/100m3）
        code_col = 3
        for c in range(1, ws.max_column + 1):
            v = ws.cell(1, c).value
            if v and '编号' in str(v):
                code_col = c
                break
        tpl_data = []
        for tf in tpls:
            tpl_data.append((tf.name, tf.read()))
        made = 0
        for row in range(2, ws.max_row + 1):
            raw = ws.cell(row, code_col).value
            code = '' if raw is None else str(raw).strip()
            if not code or code.lower() == 'none':
                continue  # 空行跳过，不出 None.docx
            for tname, tbytes in tpl_data:
                document = Document(io.BytesIO(tbytes))
                for col in range(1, ws.max_column + 1):
                    h = ws.cell(1, col).value
                    if h is None:
                        continue
                    val = ws.cell(row, col).value
                    sval = '' if val is None else str(val)  # 空值不写成字面 None
                    合同('{{%s}}' % str(h).strip(), sval, document)
                # 未命中检测 -> pm2 日志
                residual = set()
                for p in document.paragraphs:
                    residual.update(_re.findall(r'\{\{[^}]+\}\}', p.text))
                for t in document.tables:
                    for r in t.rows:
                        for c in r.cells:
                            residual.update(_re.findall(r'\{\{[^}]+\}\}', c.text))
                if residual:
                    print('=== 设计批量 未命中:', code, tname, sorted(residual), flush=True)
                buf = io.BytesIO()
                document.save(buf)
                stem = tname.rsplit('.', 1)[0]
                fname = '%s_%s.docx' % (code, stem)
                models.DesignDoc.objects.create(
                    code=code, template_name=stem,
                    file=ContentFile(buf.getvalue(), name=fname))
                made += 1
        print('=== 设计批量 完成: %d 份 (编号列=%d)' % (made, code_col), flush=True)
        return redirect('/home/kztqhp/')
    return render(request, 'kztqhp.html', {'error': None})


def design_delete(request):
    rid = request.GET.get('id')
    try:
        obj = models.DesignDoc.objects.get(id=rid)
        if obj.file:
            obj.file.delete(save=False)
        obj.delete()
    except models.DesignDoc.DoesNotExist:
        pass
    return redirect('/home/kztqhp/')


def design_export(request):
    """导出全部设计方案为 ZIP（参照合同 contractlabor_export_zip）"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for obj in models.DesignDoc.objects.all():
            f = obj.file
            if f and f.storage.exists(f.name):
                base = f.name.rsplit("/", 1)[-1]
                zipf.writestr("%s/%s" % (obj.code, base), f.read())
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="design_docs.zip"'
    return response
