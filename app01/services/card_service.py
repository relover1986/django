"""入井证生成服务 - 卡片生成、Excel解析、A4排版"""
import os
import json
import openpyxl
from io import BytesIO
from django.db import transaction
from app01 import models
from app01.image_utils import generate_label, generate_back_label, generate_sheets, generate_zip


def get_workers_with_photos(department=None):
    """返回有有效照片文件的人员列表（DB 记录 + 文件都存在）"""
    result = []
    qs = models.Worker.objects.filter(photo__isnull=False)
    if department:
        qs = qs.filter(department=department)
    for w in qs.order_by("id"):
        try:
            if w.photo and os.path.exists(w.photo.path):
                result.append(w)
        except (ValueError, FileNotFoundError):
            continue
    return result


def parse_excel(excel_file, department=""):
    """解析 Excel，返回导入数量"""
    data = excel_file.read()
    wb = openpyxl.load_workbook(BytesIO(data), read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        raise ValueError("Excel 为空")

    header_row = rows[0]
    start = 1 if header_row and isinstance(header_row[0], str) and "姓名" in str(header_row[0]) else 0

    imported = 0
    with transaction.atomic():
        for row in rows[start:]:
            if not row or not row[0]:
                continue
            name = str(row[0]).strip()
            job_type = str(row[1]).strip() if len(row) > 1 and row[1] else ""
            if not name:
                continue
            if not job_type:
                job_type = "爆破员"
            models.JobType.objects.get_or_create(name=job_type, defaults={"responsibilities": ""})
            models.Worker.objects.create(name=name, job_type=job_type, department=department)
            imported += 1

    if imported == 0:
        raise ValueError("未找到有效数据，请确保 Excel 包含「姓名」「工种」两列")
    return imported


def generate_all_cards(workers):
    """为所有人生成正反面单卡 BytesIO"""
    front_bufs, back_bufs = [], []
    for w in workers:
        if not w.photo or not os.path.exists(w.photo.path):
            raise FileNotFoundError(f"人员「{w.name}」的照片文件不存在，请重新上传")
        front_bufs.append(generate_label(w.photo.path, w.name, w.job_type))
        back_bufs.append(generate_back_label(w.name))
    return front_bufs, back_bufs
