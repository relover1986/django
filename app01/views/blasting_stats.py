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


@csrf_exempt


def blasting_stats(request):
    """雷管炸药台帐统计：按日期+班次+爆破员分组，班次合计"""
    from app01.services.stats_service import compute_blasting_stats
    display_rows = compute_blasting_stats()
    return render(request, 'blasting_stats.html', {'rows': display_rows})
def blasting_summary_list(request):
    """岩工报药列表"""
    from django.shortcuts import render
    from datetime import date
    shift_order = {'早':0,'早班':0,'白':0,'白班':0,'中':0,'中班':0,'晚':0,'晚班':0,'夜':1,'夜班':1}
    all_records_qs = models.BlastingSummary.objects.all().order_by('-created_at')
    # 将segments_data转为排序后的列表 [(段号, 数量), ...]
    for r in all_records_qs:
        sd = r.segments_data or {}
        r.seg_list = sorted(sd.items(), key=lambda x: int(x[0]))
    # 排序：夜班排后面
    all_records = sorted(all_records_qs, key=lambda r: (shift_order.get(r.shift, 0), -r.created_at.timestamp() if r.created_at else 0))
    # 上半部分仅显示当日数据
    today_str = date.today().strftime('%Y年%-m月%-d日')
    records = all_records_qs.filter(date=today_str)
    for r in records:
        sd = r.segments_data or {}
        r.seg_list = sorted(sd.items(), key=lambda x: int(x[0]))
    # 空字段提示
    empty_shift = all_records_qs.filter(shift='').count()
    empty_blaster = all_records_qs.filter(blaster='').count()
    warnings = []
    if empty_shift:
        warnings.append(f'有 {empty_shift} 条记录缺少班次')
    if empty_blaster:
        warnings.append(f'有 {empty_blaster} 条记录缺少爆破员')
    blasters = models.BlastingSummary.objects.exclude(blaster='').values_list('blaster', flat=True).distinct().order_by('blaster')
    return render(request, 'blasting_summary_list.html', {'records': records, 'all_records': all_records, 'blasters': blasters, 'warnings': warnings})
@csrf_exempt
def blasting_summary_add(request):
    """岩工报药添加 - 解析文本写入数据库，显示计算结果和核对状态"""
    from django.shortcuts import render
    from blasting_summary import parse_blasting_input
    import re

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if not text:
            return render(request, 'blasting_summary_add.html', {'error': '请输入台账文本'})

        blocks = [b.strip() for b in text.split('\n\n') if b.strip()]
        if not blocks:
            blocks = [text]

        results = []
        success_count = 0
        error_msgs = []
        
        for i, block in enumerate(blocks, 1):
            try:
                data = parse_blasting_input(block)
                
                missing_fields = []
                if not data['人员']:
                    missing_fields.append('人员')
                if not data['地点']:
                    missing_fields.append('地点')
                if not data['日期']:
                    missing_fields.append('日期')
                
                check_pass = data['雷管核对'] == '正确' and len(missing_fields) == 0
                
                result_item = {
                    '序号': i,
                    '班次': data.get('班次', '') or '—',
                    '人员': data['人员'] or '未识别',
                    '地点': data['地点'] or '未识别',
                    '日期': data['日期'] or '未识别',
                    '段号1_6': data['1-6段累加'],
                    '段号7以上': data['7段以后累加'],
                    '计算雷管': data['计算雷管总数'],
                    '标签雷管': data['雷管'],
                    '炸药': data['炸药'],
                    '核对状态': data['雷管核对'],
                    '核对通过': check_pass,
                    '缺少字段': missing_fields
                }
                results.append(result_item)
                
                if check_pass:
                    # 分段数据：优先用 parse_blasting_input 返回的 segments
                    segments = data.get('segments', {})
                    if not segments:
                        # 兼容旧格式：从原文正则提取
                        import re
                        pat_seg = re.compile(r'(\d+)[/\-\—\一](\d+)')
                        for match in pat_seg.finditer(block):
                            seg_num = int(match.group(1))
                            seg_cnt = int(match.group(2))
                            segments[str(seg_num)] = seg_cnt
                    models.BlastingSummary.objects.create(
                        shift=data.get('班次', ''),
                        person=data['人员'],
                        location=data['地点'],
                        date=data['日期'],
                        detonator_count=data['雷管'],
                        explosive_count=data['炸药'],
                        segments_data=segments,
                    )
                    success_count += 1
                else:
                    errs = []
                    if missing_fields:
                        errs.append('缺少' + ','.join(missing_fields))
                    if data['雷管核对'] != '正确':
                        errs.append('雷管核对失败:计算' + str(data['计算雷管总数']) + 'vs标签' + str(data['雷管']))
                    if not dyn_valid:
                        errs.append('炸药' + str(dyn) + '不是3或6的倍数')
                    error_msgs.append('第' + str(i) + '条:' + ';'.join(errs))
                    
            except Exception as e:
                error_msgs.append('第' + str(i) + '条解析失败:' + str(e))
                results.append({
                    '序号': i,
                    '人员': '解析失败',
                    '核对通过': False
                })

        return render(request, 'blasting_summary_add.html', {
            'results': results,
            'success_count': success_count,
            'total_count': len(blocks),
            'error_msgs': error_msgs,
        })

    return render(request, 'blasting_summary_add.html')
def blasting_summary_delete(request, pk):
    """删除雷管炸药台账记录"""
    from app01 import models
    models.BlastingSummary.objects.filter(pk=pk).delete()
    return redirect('/home/blasting_summary_list/')


def blasting_summary_assign_blaster(request):
    """AJAX 分配爆破员"""
    from django.http import JsonResponse
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        pk = data.get('pk')
        blaster = data.get('blaster', '')
        models.BlastingSummary.objects.filter(pk=pk).update(blaster=blaster)
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False}, status=400)



# ==================== 爆破现场记录 ====================
