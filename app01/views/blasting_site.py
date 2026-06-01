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


def blasting_site_photo_list(request):
    title = 'blasting_site_photo'
    if request.method == 'GET':
        from app01 import models
        model_fields = models.BlastingSitePhoto._meta.fields
        cols = [{'verbose_name': field.verbose_name} for field in model_fields if field.attname not in ('id', 'location')]
        cols.append({'verbose_name': '操作'})
        data = models.BlastingSitePhoto.objects.values("name", "photo", "rotated_photo", "blue_background", "red_background", "white_background", "uploaded_at").order_by('code')[:100]
        return render(request, 'blasting_site_photo_list.html', {
            'data': data,
            'cols': cols,
            'title': title,
        })



# ─── 签名识别（模型全局加载一次） ─────────────────────────
SIGNATURE_MODEL_PATH = "/root/MLX/05模型文件/sign_model.pth"
SIGNATURE_MAP_PATH = "/root/MLX/05模型文件/label_map.json"
LOW_CONF_DIR = os.path.join(settings.MEDIA_ROOT, "blasting_site_low_conf")
os.makedirs(LOW_CONF_DIR, exist_ok=True)

class SignNetMulti(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.pool = nn.MaxPool2d(2)
        self.fc1 = nn.Linear(32 * 64 * 64, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, num_classes)
    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        x = x.view(x.size(0), -1)
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

def _load_sign_model():
    with open(SIGNATURE_MAP_PATH) as f:
        label_map = json.load(f)
    idx_to_name = {int(k): v for k, v in label_map.items()}
    model = SignNetMulti(len(label_map))
    sd = torch.load(SIGNATURE_MODEL_PATH, weights_only=True, map_location='cpu')
    model.load_state_dict(sd)
    model.eval()
    return model, idx_to_name

_SIGN_MODEL, _SIGN_IDX = None, None

def 识别签名(_ocr_engine, record_img):
    """record_img: 1200px 高的记录区 BGR ndarray
       返回 (字段值字典, 低置信度文件列表)
       字段值: {'blaster': 名, 'safety_officer': 名, 'engineer': 名}
       未识别或低置信度的字段值为 ''
    """
    global _SIGN_MODEL, _SIGN_IDX
    if _SIGN_MODEL is None:
        _SIGN_MODEL, _SIGN_IDX = _load_sign_model()

    result = {}
    low_conf_files = []

    def _ocr(img_bgr):
        _, tmp = tempfile.mkstemp(suffix='.jpg')
        cv2.imwrite(tmp, img_bgr)
        res, _ = _ocr_engine(tmp)
        os.unlink(tmp)
        return res or []

    def _crop_sig(img, keyword, pad=220):
        h, w = img.shape[:2]
        # 固定矩形坐标 (x1, y1, x2, y2)
        if isinstance(keyword, tuple) and len(keyword) == 4:
            x1, y1, x2, y2 = keyword
            x1 = max(x1, 0); y1 = max(y1, 0)
            x2 = min(x2, w); y2 = min(y2, h)
            if x2 > x1 and y2 > y1:
                return img[y1:y2, x1:x2]
            return None
        for box, text, conf in _ocr(img):
            if keyword in text:
                pts = np.array(box, dtype=np.int32)
                xs, ys = pts[:, 0], pts[:, 1]
                y_top = max(int(ys.min()) - 10, 0)
                y_bot = min(int(ys.max()) + 10, h)
                x_r = int(xs.max())
                x_end = min(x_r + pad, w)
                return img[y_top:y_bot, x_r:x_end]
        return None

    def _predict(pil_crop):
        arr = np.array(pil_crop.convert("L"), dtype=np.float32)
        binary = np.where(arr > 130, 255, 0).astype(np.uint8)
        pb = Image.fromarray(binary)
        w, h = pb.size
        scale = 256 / max(w, h)
        nw, nh = int(w * scale), int(h * scale)
        rs = pb.resize((nw, nh), Image.LANCZOS)
        cv = Image.new("L", (256, 256), 255)
        cv.paste(rs, ((256 - nw) // 2, (256 - nh) // 2))
        final = np.array(cv, dtype=np.float32) / 255.0
        final = np.expand_dims(final, axis=0)
        x = torch.from_numpy(final).unsqueeze(0)
        with torch.no_grad():
            logits = _SIGN_MODEL(x)
            probs = torch.softmax(logits, dim=1)[0]
        pred = int(torch.argmax(logits, dim=1)[0].item())
        conf = float(probs[pred].item())
        return _SIGN_IDX[pred], conf

    # 关键词 → DB字段映射
    print(f"[签名识别] 图片尺寸: {record_img.shape[1]}x{record_img.shape[0]}")
    # 先看看 OCR 能找到什么
    all_texts = [t for _,t,_ in _ocr(record_img)]
    print(f"[签名识别] OCR共{len(all_texts)}个文字块: {all_texts[:15]}")

    configs = [
        ((160, 110, 310, 170), 0, 'blaster'),
        ('安全员', 220, 'safety_officer'),
        ('现场负责人', 220, 'engineer'),
    ]

    for keyword, pad, field in configs:
        print(f"[签名识别] 搜索关键词: {keyword}")
        crop = _crop_sig(record_img, keyword, pad)
        if crop is None:
            print(f"[签名识别]   -> 未找到 {keyword}")
        if crop is None:
            result[field] = ''
            continue
        crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        pil_crop = Image.fromarray(crop_rgb)
        pred_name, conf = _predict(pil_crop)
        print(f"[签名识别]   -> {keyword} 裁图 {crop.shape[1]}x{crop.shape[0]}, 预测={pred_name}, 置信度={conf:.1%}")
        if conf >= 0.85:
            result[field] = pred_name
        else:
            result[field] = ''
            # 保存低置信度裁图
            # 用时间戳避免重名，不用 % 避免 URL 解析错误
            import time
            fname = f"lowconf_{int(time.time()*1000)}_{keyword}_{pred_name}_{conf*100:.0f}pct.jpg"
            path = os.path.join(LOW_CONF_DIR, fname)
            cv2.imwrite(path, crop)
            low_conf_files.append(path)

    return result, low_conf_files
def blasting_site_photo_add(request):
    title = 'blasting_site_photo'
    if request.method == 'POST':
        from app01 import models
        import cv2, tempfile, os
        import numpy as np
        from django.core.files.base import ContentFile
        from deskew import determine_skew

        ocr_engine = RapidOCR()
        files = request.FILES.getlist('file')
        location = request.POST.get('location', '')
        blaster = request.POST.get('blaster', '')
        safety_officer = request.POST.get('safety_officer', '')
        engineer = request.POST.get('engineer', '')

        def 回正(img):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            angle = determine_skew(gray)
            h, w = img.shape[:2]
            M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
            return cv2.warpAffine(img, M, (w, h),
                                  flags=cv2.INTER_CUBIC,
                                  borderMode=cv2.BORDER_REPLICATE)

        def 处理单张(img):
            ident = ''
            # Step 1: 回正
            img = 回正(img)
            h, w = img.shape[:2]
            # Step 2: OCR全图定位关键文字
            _, tmp = tempfile.mkstemp(suffix='.jpg')
            cv2.imwrite(tmp, img)
            result, _ = ocr_engine(tmp)
            os.unlink(tmp)

            top_y, left_x, bottom_y = 0, 0, h
            for box, text, conf in result or []:
                pts = np.array(box, dtype=np.int32)
                xs = pts[:, 0]
                ys = pts[:, 1]
                if '爆破现场记录' in text:
                    ident = text.split("录")[1].zfill(7)
                    top_y = int(ys.min())
                if '作业场地' in text:
                    left_x = int(xs.min())
                if '存根' in text:
                    bottom_y = int(ys.max())

            # Step 3: 根据 OCR 定位裁图
            top_y = max(top_y, 0)
            left_x = max(left_x, 0)
            bottom_y = min(bottom_y, h)
            if bottom_y - top_y >= 10 and w - left_x >= 10:
                img = img[top_y:bottom_y, left_x:w]
            return img, ident

        for file in files:
            time.sleep(0.1)
            file_bytes = np.frombuffer(file.read(), np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            if img is None:
                file.seek(0)
                models.BlastingSitePhoto.objects.create(
                    location=location, photo=file, code='',
                    blaster=blaster, safety_officer=safety_officer, engineer=engineer
                )
                continue

            processed_img, ident = 处理单张(img)

            # 统一高度为 1200px（等比例缩放）
            h, w = processed_img.shape[:2]
            if h != 1200:
                new_w = int(w * 1200 / h)
                processed_img = cv2.resize(processed_img, (new_w, 1200), interpolation=cv2.INTER_LANCZOS4)

            # ── 签名识别 ──
            sig_result, low_conf_list = 识别签名(ocr_engine, processed_img)
            if low_conf_list:
                print(f"[签名] {len(low_conf_list)} 张低置信度裁图 -> {LOW_CONF_DIR}")

            # RapidOCR 定位"爆破现场记录"文字块，右侧+50像素裁切
            _, _tmp2 = tempfile.mkstemp(suffix='.jpg')
            cv2.imwrite(_tmp2, processed_img)
            _res2, _ = ocr_engine(_tmp2)
            os.unlink(_tmp2)
            _crop_right = processed_img.shape[1]
            for _box, _text, _conf in _res2 or []:
                if '爆破现场记录' in _text:
                    _pts = np.array(_box, dtype=np.int32)
                    _crop_right = min(int(_pts[:, 0].max()) + 50, processed_img.shape[1])
                    break
            processed_img = processed_img[:, :_crop_right]

            # JPEG压缩 quality=82
            success, encoded = cv2.imencode('.jpg', processed_img, [cv2.IMWRITE_JPEG_QUALITY, 82])
            if success:
                name = file.name.rsplit('.', 1)[0] + '.jpg'
                models.BlastingSitePhoto.objects.create(
                    location=location,
                    photo=ContentFile(encoded.tobytes(), name=name),
                    code=ident,
                    blaster=sig_result.get('blaster', ''),
                    safety_officer=sig_result.get('safety_officer', ''),
                    engineer=sig_result.get('engineer', ''),
                )
            else:
                file.seek(0)
                models.BlastingSitePhoto.objects.create(
                    location=location, photo=file, code=ident,
                    blaster=sig_result.get('blaster', ''),
                    safety_officer=sig_result.get('safety_officer', ''),
                    engineer=sig_result.get('engineer', ''),
                )

        return redirect('/home/blasting_site_photo_list')

    return render(request, 'blasting_site_photo_add.html')



def blasting_site_low_conf(request):
    """低置信度签名裁图列表"""
    import os, json
    from django.conf import settings
    low_dir = os.path.join(settings.MEDIA_ROOT, "blasting_site_low_conf")
    files = []
    if os.path.isdir(low_dir):
        for fname in sorted(os.listdir(low_dir), reverse=True):
            fpath = os.path.join(low_dir, fname)
            if os.path.isfile(fpath):
                size = os.path.getsize(fpath)
                files.append({'name': fname, 'size': size})
    # 读取 label_map.json 作为姓名下拉选项
    label_map_path = '/root/MLX/05模型文件/label_map.json'
    name_options = []
    try:
        with open(label_map_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for v in data.values("name", "photo", "rotated_photo", "blue_background", "red_background", "white_background", "uploaded_at"):
                if v.strip():
                    name_options.append(v.strip())
    except Exception:
        name_options = []
    return render(request, 'blasting_site_low_conf.html', {'files': files, 'name_options': name_options})


def blasting_site_photo_delete(request):
    id = request.GET.get('id')
    from app01 import models
    models.BlastingSitePhoto.objects.filter(id=str(id)).delete()
    return redirect('/home/blasting_site_photo_list')

def blasting_site_low_conf_delete(request):
    """删除低置信度签名裁图"""
    import os
    from django.conf import settings
    from django.shortcuts import redirect
    filename = request.GET.get('filename')
    if filename:
        fpath = os.path.join(settings.MEDIA_ROOT, 'blasting_site_low_conf', filename)
        if os.path.isfile(fpath):
            os.remove(fpath)
    return redirect('/home/blasting_site_low_conf/')


def blasting_site_low_conf_submit(request):
    """提交低置信度裁图到对应签名文件夹"""
    import os, json
    from django.conf import settings
    from django.http import JsonResponse
    from django.views.decorators.csrf import csrf_exempt

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': '仅支持POST'})

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'JSON解析失败'})

    items = data.get('items', [])
    if not items:
        return JsonResponse({'success': False, 'message': '没有提交项'})

    src_dir = os.path.join(settings.MEDIA_ROOT, 'blasting_site_low_conf')
    dst_root = os.path.join(settings.MEDIA_ROOT, '签名')
    moved = 0
    errors = []

    for item in items:
        filename = item.get('filename', '').strip()
        name = item.get('name', '').strip()
        if not filename or not name:
            errors.append(f'{filename or "?"}: 姓名列为空')
            continue

        src_path = os.path.join(src_dir, filename)
        if not os.path.isfile(src_path):
            errors.append(f'{filename}: 源文件不存在')
            continue

        dst_dir = os.path.join(dst_root, name)
        os.makedirs(dst_dir, exist_ok=True)

        dst_path = os.path.join(dst_dir, filename)
        if os.path.exists(dst_path):
            base, ext = os.path.splitext(filename)
            import time
            dst_path = os.path.join(dst_dir, f'{base}_{int(time.time())}{ext}')

        os.rename(src_path, dst_path)
        moved += 1

    return JsonResponse({
        'success': True,
        'moved': moved,
        'errors': errors,
    })



# ─── 签名训练（SSE 流式推送进度） ────────────────────
SIGNATURE_DATA_DIR = os.path.join(settings.MEDIA_ROOT, "签名")
SIGNATURE_OUT_DIR = "/root/MLX/05模型文件"
os.makedirs(SIGNATURE_OUT_DIR, exist_ok=True)

TARGET_SIZE_TRAIN = 256
EPOCHS_TRAIN = 40
BATCH_SIZE_TRAIN = 16
LR_TRAIN = 1e-3
POS_COUNT_TRAIN = 50
NEG_COUNT_TRAIN = 75


def _preprocess_signature(img_path):
    from PIL import Image
    img = Image.open(img_path).convert("L")
    arr = np.array(img, dtype=np.uint8)
    binary = np.where(arr > 130, 255, 0).astype(np.uint8)
    pil_bin = Image.fromarray(binary)
    w, h = pil_bin.size
    scale = TARGET_SIZE_TRAIN / max(w, h)
    nw, nh = int(w * scale), int(h * scale)
    resized = pil_bin.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("L", (TARGET_SIZE_TRAIN, TARGET_SIZE_TRAIN), 255)
    ox = (TARGET_SIZE_TRAIN - nw) // 2
    oy = (TARGET_SIZE_TRAIN - nh) // 2
    canvas.paste(resized, (ox, oy))
    final = np.array(canvas, dtype=np.float32) / 255.0
    final = np.expand_dims(final, axis=0)
    return final


def _train_sse_events():
    import random, time, glob

    data_dir = SIGNATURE_DATA_DIR
    if not os.path.isdir(data_dir):
        yield "data: " + json.dumps({"type": "error", "message": "签名目录不存在"}) + "\n\n"
        return

    person_dirs = sorted([
        d for d in os.listdir(data_dir)
        if os.path.isdir(os.path.join(data_dir, d))
    ])
    all_people = {}
    for name in person_dirs:
        d = os.path.join(data_dir, name)
        files = sorted(glob.glob(os.path.join(d, "*")))
        files = [f for f in files if os.path.isfile(f)
                 and not os.path.basename(f).startswith(".")]
        files = files[:POS_COUNT_TRAIN]
        if files:
            all_people[name] = files

    names = sorted(all_people.keys())
    num_classes = len(names)
    if num_classes < 2:
        yield "data: " + json.dumps({"type": "error", "message": "至少需要 2 人才能训练"}) + "\n\n"
        return

    label_map = {str(i): n for i, n in enumerate(names)}
    name_to_idx = {n: i for i, n in enumerate(names)}

    details = []
    for name in names:
        details.append(name + ": " + str(len(all_people[name])) + " 张")

    yield "data: " + json.dumps({"type": "start", "num_classes": num_classes, "details": details}) + "\n\n"

    # 预分配 numpy 数组，避免 list→array 双倍内存
    total_estimate = len(names) * (POS_COUNT_TRAIN + NEG_COUNT_TRAIN)
    all_imgs = np.zeros((total_estimate, 1, TARGET_SIZE_TRAIN, TARGET_SIZE_TRAIN), dtype=np.float32)
    all_labels = np.zeros(total_estimate, dtype=np.int64)
    _idx = 0
    for person_name in names:
        pos_files = all_people[person_name]
        neg_pool = []
        for other_name in names:
            if other_name != person_name:
                for f in all_people[other_name]:
                    neg_pool.append((f, name_to_idx[other_name]))
        neg_selected = random.sample(neg_pool, min(NEG_COUNT_TRAIN, len(neg_pool)))
        for f in pos_files:
            try:
                all_imgs[_idx] = _preprocess_signature(f)
                all_labels[_idx] = name_to_idx[person_name]
                _idx += 1
            except Exception:
                pass
        for f_path, label in neg_selected:
            try:
                all_imgs[_idx] = _preprocess_signature(f_path)
                all_labels[_idx] = label
                _idx += 1
            except Exception:
                pass

    total = _idx
    all_imgs = all_imgs[:total]
    all_labels = all_labels[:total]

    indices = np.random.permutation(total)
    x_np = all_imgs[indices]
    y_np = all_labels[indices]
    x_t = torch.from_numpy(x_np)
    y_t = torch.from_numpy(y_np).long()

    model = SignNetMulti(num_classes)
    loss_fn = nn.CrossEntropyLoss()
    opt = torch.optim.Adam(model.parameters(), lr=LR_TRAIN)

    start = time.time()
    batch_size = min(BATCH_SIZE_TRAIN, total)

    for epoch in range(EPOCHS_TRAIN):
        perm = torch.randperm(total)
        epoch_loss = 0.0
        n_batches = 0
        model.train()
        for i in range(0, total, batch_size):
            idx = perm[i:i + batch_size]
            bx = x_t[idx]
            by = y_t[idx]
            opt.zero_grad()
            logits = model(bx)
            loss = loss_fn(logits, by)
            loss.backward()
            opt.step()
            epoch_loss += loss.item()
            n_batches += 1
        avg_loss = epoch_loss / n_batches

        should_report = (epoch + 1) % 5 == 0 or epoch == 0 or epoch == EPOCHS_TRAIN - 1
        if should_report:
            model.eval()
            with torch.no_grad():
                correct = 0
                eval_bs = 32
                for j in range(0, total, eval_bs):
                    logits = model(x_t[j:j+eval_bs])
                    correct += (torch.argmax(logits, dim=1) == y_t[j:j+eval_bs]).sum().item()
                acc = correct / total
            log_line = "epoch {:2d}/{} | loss: {:.4f} | acc: {:.2%}".format(epoch+1, EPOCHS_TRAIN, avg_loss, acc)
            pct = round((epoch + 1) / EPOCHS_TRAIN * 100, 1)
            yield "data: " + json.dumps({
                "type": "progress", "epoch": epoch + 1, "total": EPOCHS_TRAIN,
                "loss": round(avg_loss, 4), "acc": round(acc, 4),
                "pct": pct, "log": log_line
            }) + "\n\n"

    elapsed = time.time() - start
    model.eval()
    with torch.no_grad():
        correct = 0
        eval_bs = 32
        for j in range(0, total, eval_bs):
            logits = model(x_t[j:j+eval_bs])
            correct += (torch.argmax(logits, dim=1) == y_t[j:j+eval_bs]).sum().item()
        final_acc = correct / total

    model_pth = os.path.join(SIGNATURE_OUT_DIR, "sign_model.pth")
    map_path = os.path.join(SIGNATURE_OUT_DIR, "label_map.json")
    torch.save(model.state_dict(), model_pth)
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump(label_map, f, ensure_ascii=False, indent=2)

    global _SIGN_MODEL, _SIGN_IDX
    _SIGN_MODEL = None
    _SIGN_IDX = None

    yield "data: " + json.dumps({
        "type": "done", "final_acc": round(final_acc, 4),
        "elapsed": round(elapsed, 2), "num_classes": num_classes,
        "total_samples": total
    }) + "\n\n"


def blasting_site_train_signatures(request):
    from django.http import StreamingHttpResponse
    response = StreamingHttpResponse(_train_sse_events(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


# ============================================================
# 人员管理（新）— Staff / CertType / StaffCert / StaffCertFile
# ============================================================
