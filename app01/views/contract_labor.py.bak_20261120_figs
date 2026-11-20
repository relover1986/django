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
import time as _time_mod

DESIGN_VER = 'design-v5-nameclean'


def _eval_xlsx_formula(f):
    """把简单 Excel 公式算成数值（ROUND / SUM / 四则）；算不了返回 None。"""
    import re as _rx
    try:
        expr = str(f).lstrip('=').strip()
        m = _rx.fullmatch(r'(?i)ROUND\(\s*(.+?)\s*,\s*(-?\d+)\s*\)', expr)
        if m:
            v = _eval_xlsx_formula('=' + m.group(1))
            return None if v is None else round(float(v), int(m.group(2)))
        m = _rx.fullmatch(r'(?i)SUM\(\s*(.*?)\s*\)', expr)
        if m:
            total = 0.0
            for part in m.group(1).split(','):
                v = _eval_xlsx_formula('=' + part)
                total += float(v or 0)
            return total
        if _rx.fullmatch(r'[\d\.\+\-\*/\(\)\s]+', expr):
            return eval(expr, {'__builtins__': {}}, {})
    except Exception:
        return None
    return None


def _open_xlsx_pair(fobj):
    """返回 (缓存值表, 公式表)：公式单元格优先取缓存值，没有缓存再求值。"""
    import io as _io
    fobj.seek(0)
    raw = fobj.read()
    fobj.seek(0)
    ws_v = load_workbook(_io.BytesIO(raw), data_only=True).worksheets[0]
    ws_f = load_workbook(_io.BytesIO(raw), data_only=False).worksheets[0]
    return ws_v, ws_f


def _cell_value(ws_v, ws_f, r, c):
    v = ws_v.cell(r, c).value
    if v is None:
        fv = ws_f.cell(r, c).value
        if isinstance(fv, str) and fv.strip().startswith('='):
            ev = _eval_xlsx_formula(fv)
            if ev is not None:
                v = ev
            else:
                print('=== 公式未能求值(按空值处理): R%dC%d %r' % (r, c, fv[:100]), flush=True)
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return v
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
                合同(str(ws.cell(1, table_col).value), cell_text(
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
    """设计批量处理 — 按行出（每行 x 每个模板各一份）；
    第二个 Excel（爆破参数设计表）整表插入模板的 {{table}} 位置。"""
    import re as _re

    def read_table_xlsx(fobj):
        ws_, ws_f_ = _open_xlsx_pair(fobj)
        ncol_ = ws_.max_column

        def row_vals(r):
            return [cell_text(_cell_value(ws_, ws_f_, r, c)) for c in range(1, ncol_ + 1)]

        # 第 1 行若只有 1 个非空格 -> 视为大标题行，表头在第 2 行
        first = row_vals(1)
        filled = [i for i, v in enumerate(first) if str(v).strip()]
        if len(filled) == 1:
            title_ = str(first[filled[0]]).strip()
            headers_ = row_vals(2)
            start_ = 3
        else:
            title_ = None
            headers_ = first
            start_ = 2
        rows_ = []
        for r in range(start_, ws_.max_row + 1):
            vals = row_vals(r)
            if any(str(v).strip() for v in vals):
                rows_.append(vals)
        return title_, headers_, rows_

    if request.method == 'POST':
        data_files = [f for f in request.FILES.getlist('file_data')
                      if f.name.lower().endswith('.xlsx')]
        table_files = [f for f in request.FILES.getlist('file_table')
                       if f.name.lower().endswith('.xlsx')]
        tpls = [f for f in request.FILES.getlist('file')
                if f.name.lower().endswith('.docx')]
        # 兼容旧表单：xlsx 全塞在 file 里 → 第 1 个当数据、第 2 个当表格
        if not data_files:
            allx = [f for f in request.FILES.getlist('file')
                    if f.name.lower().endswith('.xlsx')]
            data_files = allx[:1]
            if not table_files:
                table_files = allx[1:2]
        if not data_files or not tpls:
            return render(request, 'kztqhp.html',
                          {'error': '请上传 1 个数据 Excel(.xlsx) 和至少 1 个 Word 模板(.docx)；爆破参数设计表 Excel 可选'})
        # 上传指纹：用于核对"这次到底用了哪份文件/哪个进程的代码"
        import hashlib as _hl
        _db = data_files[0].read()
        data_files[0].seek(0)
        _tb = table_files[0].read() if table_files else b''
        if table_files:
            table_files[0].seek(0)
        print('=== 设计批量 上传: ver=%s pid=%d data=%s(%dB,md5=%s) table=%s(%dB,md5=%s) tpls=%s'
              % (DESIGN_VER, os.getpid(), data_files[0].name, len(_db), _hl.md5(_db).hexdigest()[:10],
                 table_files[0].name if table_files else '-', len(_tb), _hl.md5(_tb).hexdigest()[:10],
                 [f.name for f in tpls]), flush=True)
        ws, ws_f = _open_xlsx_pair(data_files[0])
        # 编号列：表头含「编号」优先，否则第3列（合同姓名位；实测该列即 45m3/100m3）
        code_col = 3
        for c in range(1, ws.max_column + 1):
            v = _cell_value(ws, ws_f, 1, c)
            if v and '编号' in str(v):
                code_col = c
                break
        # 表格 Excel：整表（含表头）插入 {{table}}
        table_title = None
        table_headers = None
        table_rows = None
        if table_files:
            table_title, table_headers, table_rows = read_table_xlsx(table_files[0])
        tpl_data = []
        for tf in tpls:
            tpl_data.append((tf.name, tf.read()))
        made = 0
        # v4：只取数据区最后一条非空行生成文档（其余逻辑不变）
        _last_row = None
        for _r in range(2, ws.max_row + 1):
            _rv = _cell_value(ws, ws_f, _r, code_col)
            _cv = '' if _rv is None else str(_rv).strip()
            if _cv and _cv.lower() != 'none':
                _last_row = _r
        for row in ([_last_row] if _last_row else []):
            raw = _cell_value(ws, ws_f, row, code_col)
            code = '' if raw is None else str(raw).strip()
            if not code or code.lower() == 'none':
                continue  # 空行跳过，不出 None.docx
            for tname, tbytes in tpl_data:
                document = Document(io.BytesIO(tbytes))
                for col in range(1, ws.max_column + 1):
                    h = _cell_value(ws, ws_f, 1, col)
                    if h is None:
                        continue
                    val = _cell_value(ws, ws_f, row, col)
                    sval = cell_text(val)  # 空值不写成字面 None；日期只留纯日期
                    合同('{{%s}}' % str(h).strip(), sval, document)
                # 表格插入（模板里必须有独占一段的 {{table}}）
                if table_headers:
                    try:
                        if not replace_table_placeholder(document, table_headers, table_rows,
                                                        title=table_title or '爆破参数设计表'):
                            print('=== 设计批量 {{table}} 未命中:', code, tname, flush=True)
                    except Exception as e:
                        print('=== 设计批量 {{table}} 失败:', code, tname, repr(e), flush=True)
                # 未命中检测 -> pm2 日志
                residual = set()
                for p in document.paragraphs:
                    residual.update(_re.findall(r'\{\{[^}]+\}\}', p.text))
                for t in document.tables:
                    for r in t.rows:
                        for c in r.cells:
                            residual.update(_re.findall(r'\{\{[^}]+\}\}', c.text))
                if residual:
                    # {{取整}}：数据 Excel 没有这一列时，从「总装药量」单元格取数字四舍五入
                    if '{{取整}}' in residual:
                        total_col = None
                        for c in range(1, ws.max_column + 1):
                            hv = _cell_value(ws, ws_f, 1, c)
                            if hv and '总装药量' in str(hv):
                                total_col = c
                                break
                        if total_col:
                            raw_total = cell_text(_cell_value(ws, ws_f, row, total_col))
                            m = _re.search(r'\d+(?:\.\d+)?', raw_total)
                            if m:
                                合同('{{取整}}', str(int(round(float(m.group())))), document)
                                residual.discard('{{取整}}')
                if residual:
                    print('=== 设计批量 未命中:', code, tname, sorted(residual), flush=True)
                buf = io.BytesIO()
                document.save(buf)
                stem = tname.rsplit('.', 1)[0]
                # 生成命名去掉模板名前缀「模板-」/「模板_」/「模板」
                stem_out = _re.sub(r'^模板[\-_－—\s]*', '', stem).strip() or stem
                fname = '%s_%s_%s.docx' % (code, stem_out, _time_mod.strftime('%m%d_%H%M%S'))
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
