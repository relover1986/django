"""
爆破现场签名识别服务
从 blasting_site.py 抽离的 ML 相关逻辑
PyTorch import 采用懒加载（仅在函数内部 import）
"""

import json
import os
import numpy as np
from PIL import Image
from django.conf import settings

# ─── 路径 & 常量 ─────────────────────────
SIGNATURE_MODEL_PATH = "/root/django/models/sign_model.pth"
SIGNATURE_MAP_PATH = "/root/MLX/05模型文件/label_map.json"
LOW_CONF_DIR = os.path.join(settings.MEDIA_ROOT, "blasting_site_low_conf")
os.makedirs(LOW_CONF_DIR, exist_ok=True)

SIGNATURE_DATA_DIR = os.path.join(settings.MEDIA_ROOT, "签名")
SIGNATURE_OUT_DIR = "/root/MLX/05模型文件"
os.makedirs(SIGNATURE_OUT_DIR, exist_ok=True)

TARGET_SIZE_TRAIN = 256
EPOCHS_TRAIN = 40
BATCH_SIZE_TRAIN = 16
LR_TRAIN = 1e-3
POS_COUNT_TRAIN = 50
NEG_COUNT_TRAIN = 75

# 全局模型缓存
_SIGN_MODEL = None
_SIGN_IDX = None


class SignNetMulti:
    """神经网络定义 — PyTorch 懒加载"""

    def __init__(self, num_classes):
        import torch.nn as nn
        import torch

        self.conv1 = nn.Conv2d(1, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.pool = nn.MaxPool2d(2)
        self.fc1 = nn.Linear(32 * 64 * 64, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, num_classes)
        self._nn = nn
        self._torch = torch

    def forward(self, x):
        x = self._nn.functional.relu(self.conv1(x))
        x = self.pool(x)
        x = self._nn.functional.relu(self.conv2(x))
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        x = self._nn.functional.relu(self.fc1(x))
        x = self._nn.functional.relu(self.fc2(x))
        return self.fc3(x)

    def __call__(self, x):
        return self.forward(x)


def _load_sign_model():
    """加载签名模型，检查模型文件路径是否存在"""
    import torch

    if not os.path.exists(SIGNATURE_MODEL_PATH):
        raise FileNotFoundError(
            f"签名模型文件不存在: {SIGNATURE_MODEL_PATH}"
        )

    import torch.nn as nn

    with open(SIGNATURE_MAP_PATH, encoding="utf-8") as f:
        label_map = json.load(f)
    idx_to_name = {int(k): v for k, v in label_map.items()}
    model = SignNetMulti(len(label_map))
    sd = torch.load(SIGNATURE_MODEL_PATH, weights_only=True, map_location="cpu")
    model.load_state_dict(sd)
    model.eval()
    return model, idx_to_name


def 识别签名(_ocr_engine, record_img):
    """record_img: 1200px 高的记录区 BGR ndarray
       返回 (字段值字典, 低置信度文件列表)
       字段值: {'blaster': 名, 'safety_officer': 名, 'engineer': 名}
       未识别或低置信度的字段值为 ''
    """
    import torch
    import cv2
    import tempfile
    import time as _time

    global _SIGN_MODEL, _SIGN_IDX
    if _SIGN_MODEL is None:
        _SIGN_MODEL, _SIGN_IDX = _load_sign_model()

    result = {}
    low_conf_files = []

    def _ocr(img_bgr):
        _, tmp = tempfile.mkstemp(suffix=".jpg")
        cv2.imwrite(tmp, img_bgr)
        res, _ = _ocr_engine(tmp)
        os.unlink(tmp)
        return res or []

    def _crop_sig(img, keyword, pad=220):
        h, w = img.shape[:2]
        if isinstance(keyword, tuple) and len(keyword) == 4:
            x1, y1, x2, y2 = keyword
            x1 = max(x1, 0)
            y1 = max(y1, 0)
            x2 = min(x2, w)
            y2 = min(y2, h)
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

    print(f"[签名识别] 图片尺寸: {record_img.shape[1]}x{record_img.shape[0]}")
    all_texts = [t for _, t, _ in _ocr(record_img)]
    print(f"[签名识别] OCR共{len(all_texts)}个文字块: {all_texts[:15]}")

    configs = [
        ((160, 110, 310, 170), 0, "blaster"),
        ("安全员", 220, "safety_officer"),
        ("现场负责人", 220, "engineer"),
    ]

    for keyword, pad, field in configs:
        print(f"[签名识别] 搜索关键词: {keyword}")
        crop = _crop_sig(record_img, keyword, pad)
        if crop is None:
            print(f"[签名识别]   -> 未找到 {keyword}")
            result[field] = ""
            continue
        crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        pil_crop = Image.fromarray(crop_rgb)
        pred_name, conf = _predict(pil_crop)
        print(
            f"[签名识别]   -> {keyword} 裁图 {crop.shape[1]}x{crop.shape[0]}, 预测={pred_name}, 置信度={conf:.1%}"
        )
        if conf >= 0.85:
            result[field] = pred_name
        else:
            result[field] = ""
            fname = f"lowconf_{int(_time.time()*1000)}_{keyword}_{pred_name}_{conf*100:.0f}pct.jpg"
            path = os.path.join(LOW_CONF_DIR, fname)
            cv2.imwrite(path, crop)
            low_conf_files.append(path)

    return result, low_conf_files


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
    import random
    import time
    import glob
    import torch
    import torch.nn as nn

    data_dir = SIGNATURE_DATA_DIR
    if not os.path.isdir(data_dir):
        yield "data: " + json.dumps({"type": "error", "message": "签名目录不存在"}) + "\n\n"
        return

    person_dirs = sorted(
        [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
    )
    all_people = {}
    for name in person_dirs:
        d = os.path.join(data_dir, name)
        files = sorted(glob.glob(os.path.join(d, "*")))
        files = [
            f
            for f in files
            if os.path.isfile(f) and not os.path.basename(f).startswith(".")
        ]
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

    total_estimate = len(names) * (POS_COUNT_TRAIN + NEG_COUNT_TRAIN)
    all_imgs = np.zeros(
        (total_estimate, 1, TARGET_SIZE_TRAIN, TARGET_SIZE_TRAIN), dtype=np.float32
    )
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
            idx = perm[i : i + batch_size]
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
                    logits = model(x_t[j : j + eval_bs])
                    correct += (
                        (torch.argmax(logits, dim=1) == y_t[j : j + eval_bs])
                        .sum()
                        .item()
                    )
                acc = correct / total
            log_line = "epoch {:2d}/{} | loss: {:.4f} | acc: {:.2%}".format(
                epoch + 1, EPOCHS_TRAIN, avg_loss, acc
            )
            pct = round((epoch + 1) / EPOCHS_TRAIN * 100, 1)
            yield "data: " + json.dumps(
                {
                    "type": "progress",
                    "epoch": epoch + 1,
                    "total": EPOCHS_TRAIN,
                    "loss": round(avg_loss, 4),
                    "acc": round(acc, 4),
                    "pct": pct,
                    "log": log_line,
                }
            ) + "\n\n"

    elapsed = time.time() - start
    model.eval()
    with torch.no_grad():
        correct = 0
        eval_bs = 32
        for j in range(0, total, eval_bs):
            logits = model(x_t[j : j + eval_bs])
            correct += (
                (torch.argmax(logits, dim=1) == y_t[j : j + eval_bs]).sum().item()
            )
        final_acc = correct / total

    model_pth = os.path.join(SIGNATURE_OUT_DIR, "sign_model.pth")
    map_path = os.path.join(SIGNATURE_OUT_DIR, "label_map.json")
    torch.save(model.state_dict(), model_pth)
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump(label_map, f, ensure_ascii=False, indent=2)

    global _SIGN_MODEL, _SIGN_IDX
    _SIGN_MODEL = None
    _SIGN_IDX = None

    yield "data: " + json.dumps(
        {
            "type": "done",
            "final_acc": round(final_acc, 4),
            "elapsed": round(elapsed, 2),
            "num_classes": num_classes,
            "total_samples": total,
        }
    ) + "\n\n"
