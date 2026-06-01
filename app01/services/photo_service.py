"""照片处理服务 - 百度AI人像分割、背景替换、排版"""
import io
import base64
import os
from PIL import Image
from django.core.files.base import ContentFile
from aip import AipBodyAnalysis
from app01.photo import resize_photo, cut_photo, 排版

# 百度API配置
APP_ID = '118049497'
API_KEY = 'AmK3oZpZhns9jAm2rJgzRyLq'
SECRET_KEY = 'LbbCCzQyv1FlytQxBHstZ5Yt5i4B7pMw'
_client = AipBodyAnalysis(APP_ID, API_KEY, SECRET_KEY)

BACKGROUND_COLORS = {
    '蓝底': (67, 142, 219),
    '红底': (255, 0, 0),
    '白底': (255, 255, 255),
}

OUTPUT_SIZE = (295, 413)  # 一寸照片标准尺寸


def body_seg(img_bytes):
    """百度AI人像分割"""
    return _client.bodySeg(img_bytes)


def process_photo_image(file_obj, filename=None):
    """处理单张照片：裁剪、缩放、人像分割、生成三种背景
    
    返回 dict: {
        'photo_bytes': bytes,
        'rotated_bytes': bytes,
        'bg_files': {'blue': ContentFile, 'red': ContentFile, 'white': ContentFile},
        'white_bg_single': ContentFile or None,
        'has_foreground': bool,
    }
    """
    img = Image.open(file_obj)
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')

    img = resize_photo(cut_photo(img, 1), 1)
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG', quality=45, optimize=True, subsampling='4:2:0')
    img_bytes = img_io.getvalue()

    if not filename:
        filename = os.path.splitext(getattr(file_obj, 'name', 'photo'))[0][:10]

    result = body_seg(img_bytes)
    has_foreground = 'foreground' in result

    bg_files = {'blue': None, 'red': None, 'white': None}
    white_bg_single_file = None

    if has_foreground:
        foreground = Image.open(io.BytesIO(base64.b64decode(result['foreground'])))
        foreground.thumbnail(OUTPUT_SIZE)

        for name, color in BACKGROUND_COLORS.items():
            background = Image.new('RGB', OUTPUT_SIZE, color)
            x = (OUTPUT_SIZE[0] - foreground.width) // 2
            y = (OUTPUT_SIZE[1] - foreground.height) // 2
            background.paste(foreground, (x, y), foreground)

            if name == '白底':
                single_io = io.BytesIO()
                background.save(single_io, format='JPEG')
                white_bg_single_file = ContentFile(single_io.getvalue(), name=f"{filename}_white_single.jpg")

            rotated_bg_io = io.BytesIO()
            排版(background, rotated_bg_io)
            rotated_bg_bytes = rotated_bg_io.getvalue()

            if name == '蓝底':
                bg_files['blue'] = ContentFile(rotated_bg_bytes, name=f"{filename}_blue.jpg")
            elif name == '红底':
                bg_files['red'] = ContentFile(rotated_bg_bytes, name=f"{filename}_red.jpg")
            elif name == '白底':
                bg_files['white'] = ContentFile(rotated_bg_bytes, name=f"{filename}_white.jpg")

    rotated_io = io.BytesIO()
    排版(img, rotated_io)
    rotated_bytes = rotated_io.getvalue()

    return {
        'photo_bytes': img_bytes,
        'rotated_bytes': rotated_bytes,
        'bg_files': bg_files,
        'white_bg_single': white_bg_single_file,
        'has_foreground': has_foreground,
    }


def generate_white_bg_single(photo_path):
    """从已有照片生成白底一寸照（不排版）"""
    img = Image.open(photo_path).convert('RGB')
    img = resize_photo(cut_photo(img, 1), 1)

    img_io = io.BytesIO()
    img.save(img_io, format='JPEG')
    img_bytes = img_io.getvalue()

    result = body_seg(img_bytes)
    if 'foreground' not in result:
        raise ValueError("bodySeg failed: no foreground")

    foreground = Image.open(io.BytesIO(base64.b64decode(result['foreground'])))
    foreground.thumbnail(OUTPUT_SIZE)

    background = Image.new("RGB", OUTPUT_SIZE, (255, 255, 255))
    x = (OUTPUT_SIZE[0] - foreground.width) // 2
    y = (OUTPUT_SIZE[1] - foreground.height) // 2
    background.paste(foreground, (x, y), foreground)

    single_io = io.BytesIO()
    background.save(single_io, format='JPEG')
    return single_io.getvalue()
