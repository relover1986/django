"""
工具服务
从 other.py 抽离的纯 PIL 图片处理函数，无 Django 依赖
"""

import io
from PIL import Image
from django.core.files.base import ContentFile


def save_image_to_field(img, filename):
    """将 PIL Image 保存为 Django ContentFile，适用于 ImageField/FIleField"""
    img_io = io.BytesIO()
    if img.mode in ("RGBA", "LA"):
        img = img.convert("RGB")
    img.save(img_io, format="JPEG")
    return ContentFile(img_io.getvalue(), name=filename)


def process_photo(img):
    """处理证件照：裁剪 + 缩放"""
    from app01.photo import cut_photo, resize_photo

    img = cut_photo(img, 1)
    img = resize_photo(img, 1)
    img_io = io.BytesIO()
    img.save(img_io, format="JPEG")
    return ContentFile(img_io.getvalue())


def apply_orientation(img, orientation):
    """根据 EXIF 方向值校正图片方向"""
    from PIL import ImageOps

    ORIENTATIONS = {
        1: (0, False),
        2: (0, True),
        3: (180, False),
        4: (180, True),
        5: (90, True),
        6: (270, False),
        7: (270, True),
        8: (90, False),
    }

    degrees, mirror = ORIENTATIONS.get(orientation, (0, False))

    if mirror:
        img = ImageOps.mirror(img)
    if degrees == 90:
        img = img.transpose(Image.ROTATE_90)
    elif degrees == 180:
        img = img.transpose(Image.ROTATE_180)
    elif degrees == 270:
        img = img.transpose(Image.ROTATE_270)

    return img.convert("RGB")  # 确保返回统一格式
