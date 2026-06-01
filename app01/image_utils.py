import os
import base64
from io import BytesIO
from math import ceil
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
import rembg

# ---------- 单卡常量 ----------
AVATAR_W, AVATAR_H = 200, 280
AVATAR_X, AVATAR_Y = 160, 25

CARD_W, CARD_H = 856, 540

TITLE_FONT_SIZE = 66
NAME_FONT_SIZE = 42
INFO_FONT_SIZE = 36
BACK_NAME_SIZE = 110       # 大字
BACK_MSG_SIZE = 96         # 大字

BG_COLOR_MAP = {
    "white": (255, 255, 255),
    "blue":  (0, 112, 192),
    "red":   (237, 28, 36),
}

UNIT_TEXT = "单位：辽宁捷祥矿业工程公司"
PROJ_TEXT = "驻宏鹏矿业项目部"

# ---------- A4 排版常量 ----------
A4_W, A4_H = 2100, 2970
PAIR_PER_PAGE = 5           # 每页5人（左正右背）

_GAP_X = (A4_W - 2 * CARD_W) // 3  # 129
_GAP_Y = (A4_H - PAIR_PER_PAGE * CARD_H) // (PAIR_PER_PAGE + 1)  # 45
BORDER_WIDTH = 4

# ---------- 字体 ----------
_FONT_CANDIDATES = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "C:/Windows/Fonts/simhei.ttf",
]
_BOLD_CANDIDATES = [
    "/System/Library/Fonts/STHeiti Bold.ttc",
    "/System/Library/Fonts/Supplemental/STHeiti Bold.ttc",
    "/System/Library/Fonts/PingFang.ttc",
]


def _parse_hex_color(hex_color: str) -> tuple:
    """解析 #RRGGBB 格式为 (R, G, B) 元组"""
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def apply_photo_background(photo_path: str, bg_mode: str = "none", bg_color: str = "") -> Image.Image:
    """根据 bg_mode 处理头像背景，本地 rembg 模型，不调用 API"""
    img = Image.open(photo_path)

    if bg_mode == "none":
        return img.convert("RGB")

    rgba = rembg.remove(img)

    if bg_mode == "white":
        bg_rgb = BG_COLOR_MAP["white"]
    elif bg_mode == "blue":
        bg_rgb = BG_COLOR_MAP["blue"]
    elif bg_mode == "red":
        bg_rgb = BG_COLOR_MAP["red"]
    else:
        color = bg_color if bg_color else "#2196F3"
        bg_rgb = _parse_hex_color(color)

    bg = Image.new("RGB", rgba.size, bg_rgb)
    bg.paste(rgba, (0, 0), rgba.split()[3])
    return bg


def _find_font():
    for p in _FONT_CANDIDATES:
        if os.path.exists(p):
            return p
    return None


def _load_font(size):
    path = _find_font()
    if path:
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _load_font_bold(size):
    """尝试加载粗体，回退到普通字体"""
    for p in _BOLD_CANDIDATES:
        if os.path.exists(p):
            try:
                # PingFang.ttc 中 Semibold 通常在 index 2
                return ImageFont.truetype(p, size, index=2)
            except Exception:
                return ImageFont.truetype(p, size)
    return _load_font(size)


def generate_label(photo_path: str, name: str, job_type: str) -> BytesIO:
    """正面标签：头像 + 姓名 + 工种 + 单位，856×540"""
    bg_path = os.path.join(settings.MEDIA_ROOT, "入井背景图_856x540.jpg")
    if not os.path.exists(bg_path):
        alt = os.path.join(settings.MEDIA_ROOT, "background.jpg")
        if os.path.exists(alt):
            bg_path = alt
        else:
            raise FileNotFoundError("未找到背景图")

    img = Image.open(bg_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 直接缩放照片，不做人脸对齐（照片上传时已处理过）
    photo = Image.open(photo_path).convert("RGB")
    photo_resized = photo.resize((AVATAR_W, AVATAR_H), Image.LANCZOS)
    img.paste(photo_resized, (AVATAR_X, AVATAR_Y))

    title_font = _load_font(TITLE_FONT_SIZE)
    name_font = _load_font(NAME_FONT_SIZE)
    info_font = _load_font(INFO_FONT_SIZE)

    title = "正在作业"
    tb = draw.textbbox((0, 0), title, font=title_font)
    tx = (CARD_W - tb[2] - tb[0]) // 2
    draw.text((tx + 130, 85), title, fill=(0, 0, 0), font=title_font)
    title_bottom = 35 + tb[3] + 10

    ub = draw.textbbox((0, 0), UNIT_TEXT, font=info_font)
    pb = draw.textbbox((0, 0), PROJ_TEXT, font=info_font)
    block_h = (ub[3] - ub[1]) + 10 + (pb[3] - pb[1])
    block_y_start = CARD_H - 30 - block_h

    ux = (CARD_W - ub[2] - ub[0]) // 2
    draw.text((ux, block_y_start), UNIT_TEXT, fill=(0, 0, 0), font=info_font)
    px = (CARD_W - pb[2] - pb[0]) // 2
    draw.text((px, block_y_start + (ub[3] - ub[1]) + 10), PROJ_TEXT, fill=(0, 0, 0), font=info_font)

    label_text = f"姓名：{name}              工种：{job_type}"
    nb = draw.textbbox((0, 0), label_text, font=name_font)
    name_h = nb[3] - nb[1]
    name_y = title_bottom + (block_y_start - title_bottom - name_h) // 2 + 110
    nx = (CARD_W - nb[2] - nb[0]) // 2
    draw.text((nx, name_y), label_text, fill=(0, 0, 0), font=name_font)

    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85)
    buf.seek(0)
    return buf


def generate_back_label(name: str) -> BytesIO:
    """背面标签：姓名（粗体大字）+ 现已升井，间距大，居中"""
    img = Image.new("RGB", (CARD_W, CARD_H), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    name_font = _load_font_bold(BACK_NAME_SIZE)
    msg_font = _load_font(BACK_MSG_SIZE)

    # 姓名 —— 粗体，居中偏上，距顶部约1/4
    nb = draw.textbbox((0, 0), name, font=name_font)
    nw = nb[2] - nb[0]
    nh = nb[3] - nb[1]
    nx = (CARD_W - nw) // 2
    ny = CARD_H // 4 - nh // 2
    draw.text((nx, ny), name, fill=(0, 0, 0), font=name_font, stroke_width=3)
    name_bottom = ny + nb[3]

    # "现已升井" —— 粗体，居中偏下，距底部约1/4
    msg = "现已升井"
    mb = draw.textbbox((0, 0), msg, font=msg_font)
    mw = mb[2] - mb[0]
    mx = (CARD_W - mw) // 2
    my = CARD_H * 3 // 4 - (mb[3] - mb[1]) // 2
    draw.text((mx, my), msg, fill=(0, 0, 0), font=msg_font)

    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85)
    buf.seek(0)
    return buf


def generate_sheets(workers: list, front_bufs: list[BytesIO], back_bufs: list[BytesIO]) -> list[dict]:
    """生成 A4 排版页，每页 5 人（左正右背），返回 [{name, b64_data}, ...]"""
    sheets = []
    num_pages = ceil(len(workers) / PAIR_PER_PAGE)

    for page in range(num_pages):
        sheet = Image.new("RGB", (A4_W, A4_H), (255, 255, 255))
        draw = ImageDraw.Draw(sheet)

        start = page * PAIR_PER_PAGE
        end = start + PAIR_PER_PAGE
        chunk = list(zip(workers[start:end], front_bufs[start:end], back_bufs[start:end]))

        for row_idx, (worker, f_buf, b_buf) in enumerate(chunk):
            y = _GAP_Y + row_idx * (CARD_H + _GAP_Y)

            # 左列：正面
            x_left = _GAP_X
            front = Image.open(f_buf).convert("RGB")
            sheet.paste(front, (x_left, y))
            draw.rectangle([x_left, y, x_left + CARD_W, y + CARD_H], outline="black", width=BORDER_WIDTH)

            # 右列：背面（同一人）
            x_right = _GAP_X + CARD_W + _GAP_X
            back = Image.open(b_buf).convert("RGB")
            sheet.paste(back, (x_right, y))
            draw.rectangle([x_right, y, x_right + CARD_W, y + CARD_H], outline="black", width=BORDER_WIDTH)

            # 在正面卡片右下角标注姓名（方便查看）
            label_font = _load_font(22)
            draw.text((x_left + 10, y + CARD_H - 35),
                      f"{worker.name} {worker.job_type}", fill=(100, 100, 100), font=label_font)

        out = BytesIO()
        sheet.save(out, format="JPEG", quality=90)
        out.seek(0)
        b64 = base64.b64encode(out.getvalue()).decode()

        sheets.append({
            "page": page + 1,
            "b64": b64,
            "count": len(chunk),
        })

    return sheets


def generate_zip(workers: list, front_bufs: list[BytesIO], back_bufs: list[BytesIO]) -> BytesIO:
    """生成含 A4 排版页 + 单卡的 ZIP"""
    import zipfile
    from datetime import datetime

    zip_buf = BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        num_pages = ceil(len(workers) / PAIR_PER_PAGE)

        for page in range(num_pages):
            sheet = Image.new("RGB", (A4_W, A4_H), (255, 255, 255))
            draw = ImageDraw.Draw(sheet)

            start = page * PAIR_PER_PAGE
            end = start + PAIR_PER_PAGE
            chunk = zip(workers[start:end], front_bufs[start:end], back_bufs[start:end])

            for row_idx, (worker, f_buf, b_buf) in enumerate(chunk):
                y = _GAP_Y + row_idx * (CARD_H + _GAP_Y)

                x_left = _GAP_X
                front = Image.open(f_buf).convert("RGB")
                sheet.paste(front, (x_left, y))
                draw.rectangle([x_left, y, x_left + CARD_W, y + CARD_H], outline="black", width=BORDER_WIDTH)

                x_right = _GAP_X + CARD_W + _GAP_X
                back = Image.open(b_buf).convert("RGB")
                sheet.paste(back, (x_right, y))
                draw.rectangle([x_right, y, x_right + CARD_W, y + CARD_H], outline="black", width=BORDER_WIDTH)

            out = BytesIO()
            sheet.save(out, format="JPEG", quality=90)
            zf.writestr(f"A4排版_第{page + 1}页.jpg", out.getvalue())

        # 单卡
        for w, f_buf, b_buf in zip(workers, front_bufs, back_bufs):
            zf.writestr(f"单卡/{w.name}_{w.job_type}_正面.jpg", f_buf.getvalue())
            zf.writestr(f"单卡/{w.name}_{w.job_type}_背面.jpg", b_buf.getvalue())

    zip_buf.seek(0)
    return zip_buf
