#%%
#Author:ZM
"""
照片尺寸，宽*高(单位:像素)
1寸照片:295*413
2寸照片:413*626
5寸照片(横版):1500*1050
6寸照片(横版):1800*1200
"""
from PIL import Image,ImageDraw
import os
from aip import AipOcr
import os

# 定义常量
APP_ID = '23933903'
API_KEY = 'n8UVViIuLYnmRfKAzq5z5rvf'
SECRET_KEY = 'vEowelgK61XIFbiinXITEZLMnno9HSsv'

WIDTH_sfz = 1011
HEIGHT_sfz = 639


WIDTH_1IN = 295
HEIGHT_1IN = 413

WIDTH_2IN = 413
HEIGHT_2IN = 626

WIDTH_5IN = 1500
HEIGHT_5IN = 1050

# 非全景6寸照片
WIDTH_6IN = 1950
HEIGHT_6IN = 1300


WIDTH_A4 = 2480
HEIGHT_A4 = 3508



def cut_photo(photo,choice):
    """
    将照片按照比例进行裁剪成1寸、2寸
    :param photo: 待处理的照片
    :param choice: <int> 1代表1寸，2代表2寸
    :return: 处理后的照片
    """
    width = photo.size[0] # 宽
    height = photo.size[1] #高
    rate = height / width
    if choice == 1:
        if rate < (HEIGHT_1IN/WIDTH_1IN):
            x = (width - int(height / HEIGHT_1IN * WIDTH_1IN)) / 2
            y = 0
            cutted_photo = photo.crop((x, y, x + (int(height / HEIGHT_1IN * WIDTH_1IN)), y + height))

        else:
            x = 0
            y = (height - int(width / WIDTH_1IN * HEIGHT_1IN)) / 2
            cutted_photo = photo.crop((x, y, x + width, y + (int(width / WIDTH_1IN * HEIGHT_1IN))))
        return cutted_photo

    if choice == 2:
        if rate < (HEIGHT_2IN/WIDTH_2IN):
            x = (width - int(height / HEIGHT_2IN * WIDTH_2IN)) / 2
            y = 0
            cutted_photo = photo.crop((x, y, x + (int(height / HEIGHT_2IN * WIDTH_2IN)), y + height))

        else:
            x = 0
            y = (height - int(width / WIDTH_2IN * HEIGHT_2IN)) / 2
            cutted_photo = photo.crop((x, y, x + width, y + (int(width / WIDTH_2IN * HEIGHT_2IN))))

        return cutted_photo

def resize_photo(photo,choice):
    '''
    缩放照片
    :param photo: 待处理的照片
    :param choice: <int> 1代表1寸,2代表2寸
    :return: 处理后的照片
    '''
    if choice == 1:
        resized_photo = photo.resize((WIDTH_1IN,HEIGHT_1IN))
        return resized_photo
    elif choice == 2:
        resized_photo = photo.resize((WIDTH_2IN, HEIGHT_2IN))
        return resized_photo
    elif choice == 3:
        resized_photo = photo.resize((WIDTH_sfz, HEIGHT_sfz))
        return resized_photo   
    elif choice == 4:
        resized_photo = photo.resize((WIDTH_A4, HEIGHT_A4))
        return resized_photo   


def layout_photo_5_1(photo):
    """
    在5寸照片上排版1寸照片
    :param photo: 待处理照片1寸
    :return: 处理后的照片
    """
    bk = Image.new("RGB", [WIDTH_5IN,HEIGHT_5IN], (255,255,255))
    draw = ImageDraw.Draw(bk)# 创建画笔
    draw.line([(0,HEIGHT_5IN/2),(WIDTH_5IN,HEIGHT_5IN/2)],fill=128) # 横线
    draw.line([(WIDTH_5IN*0.25,0),(WIDTH_5IN*0.25,HEIGHT_5IN)],fill=128) # 第1条竖线
    draw.line([(WIDTH_5IN*0.5,0),(WIDTH_5IN*0.5,HEIGHT_5IN)],fill=128) # 第2条竖线
    draw.line([(WIDTH_5IN*0.75,0),(WIDTH_5IN*0.75,HEIGHT_5IN)],fill=128) # 第3条竖线

    focus_point = [0.125 * WIDTH_5IN,0.25 * HEIGHT_5IN]
    start_point = [focus_point[0] - 0.5 * WIDTH_1IN, focus_point[1] - 0.5 * HEIGHT_1IN]
    for i in range(0,2):
        for k in range(0,4):
            bk.paste(photo, (int(start_point[0] + (k * WIDTH_5IN / 4)), int(start_point[1] + 0.5 * i * HEIGHT_5IN)))
    return bk


def layout_photo_5_2(photo):
    """
    在5寸照片上排版2寸照片
    :param photo: 待处理照片2寸
    :return: 处理后的照片
    """
    bk = Image.new("RGB", [HEIGHT_5IN,WIDTH_5IN], (255,255,255)) # 竖版排版
    # 创建画笔
    draw = ImageDraw.Draw(bk)
    draw.line([(0,WIDTH_5IN/2),(WIDTH_5IN,WIDTH_5IN/2)],fill=128) # 横线
    draw.line([(HEIGHT_5IN*0.5,0),(HEIGHT_5IN*0.5,WIDTH_5IN)],fill=128) # 竖线
    focus_point = [0.25 * HEIGHT_5IN, 0.25 * WIDTH_5IN]
    start_point = [focus_point[0] - 0.5 * WIDTH_2IN, focus_point[1] - 0.5 * HEIGHT_2IN]
    #print(focus_point,start_point)
    for i in range(0,2):
        for k in range(0,2):
            bk.paste(photo, (int(start_point[0] + (k * HEIGHT_5IN / 2)), int(start_point[1] + 0.5* i * WIDTH_5IN)))
    return bk

def layout_photo_5_mix(photo1,photo2):
    """
    在5寸照片上混合排版1寸、2寸照片
    :param photo1: 待处理照片1寸
    :param photo1: 待处理照片2寸
    :return: 处理后的照片
    """
    bk = Image.new("RGB", [WIDTH_5IN,HEIGHT_5IN], (255,255,255))
    # 创建画笔
    draw = ImageDraw.Draw(bk)
    draw.line([(0,HEIGHT_5IN/2),(WIDTH_5IN,HEIGHT_5IN/2)],fill=128) # 横线
    draw.line([(WIDTH_5IN*0.25,0),(WIDTH_5IN*0.25,HEIGHT_5IN)],fill=128) # 第1条竖线
    draw.line([(WIDTH_5IN*0.5,0),(WIDTH_5IN*0.5,HEIGHT_5IN)],fill=128) # 第2条竖线

    focus_point = [0.125 * WIDTH_5IN,0.25 * HEIGHT_5IN]
    start_point = [focus_point[0] - 0.5 * WIDTH_1IN, focus_point[1] - 0.5 * HEIGHT_1IN]
    focus_point2 = [0.75 * WIDTH_5IN, 0.25 * HEIGHT_5IN]
    start_point2 = [focus_point2[0] - 0.5 * HEIGHT_2IN, focus_point2[1] - 0.5 * WIDTH_2IN]

    for i in range(0,2):
        for k in range(0,2):
            bk.paste(photo1, (int(start_point[0] + (k * WIDTH_5IN / 4)), int(start_point[1] + 0.5 * i * HEIGHT_5IN)))

    bk.paste(photo2,(int(start_point2[0]),int(start_point2[1])))
    bk.paste(photo2,(int(start_point2[0]),int(start_point2[1] + 0.5 * HEIGHT_5IN)))
    return bk

def layout_photo_6_1(photo):
    """
    在6寸照片上排版2寸照片
    :param photo: 待处理照片1寸
    :return: 处理后的照片
    """
    bk = Image.new("RGB", [HEIGHT_6IN,WIDTH_6IN], (255,255,255)) # 竖版排版
    # 创建画笔
    draw = ImageDraw.Draw(bk)
    draw.line([(0,WIDTH_6IN*0.25),(WIDTH_6IN,WIDTH_6IN*0.25)],fill=128) # 横线
    draw.line([(0,WIDTH_6IN*0.5),(WIDTH_6IN,WIDTH_6IN*0.5)],fill=128) # 横线
    draw.line([(0,WIDTH_6IN*0.75),(WIDTH_6IN,WIDTH_6IN*0.75)],fill=128) # 横线
    draw.line([(HEIGHT_6IN*0.25,0),(HEIGHT_6IN*0.25,WIDTH_6IN)],fill=128) # 竖线
    draw.line([(HEIGHT_6IN*0.5,0),(HEIGHT_6IN*0.5,WIDTH_6IN)],fill=128) # 竖线
    draw.line([(HEIGHT_6IN*0.75,0),(HEIGHT_6IN*0.75,WIDTH_6IN)],fill=128) # 竖线
    focus_point = [0.125 * HEIGHT_6IN, 0.125 * WIDTH_6IN]
    start_point = [focus_point[0] - 0.5 * WIDTH_1IN, focus_point[1] - 0.5 * HEIGHT_1IN]
    #print(focus_point,start_point)
    for i in range(0,4):
        for k in range(0,4):
            bk.paste(photo, (int(start_point[0] + (k * HEIGHT_6IN / 4)), int(start_point[1] + i * 0.25 * WIDTH_6IN )))
    return bk

def layout_photo_6_2(photo):
    """
    在6寸照片上排版2寸照片
    :param photo: 待处理照片2寸
    :return: 处理后的照片
    """
    bk = Image.new("RGB", [WIDTH_6IN,HEIGHT_6IN], (255,255,255))
    # 创建画笔
    draw = ImageDraw.Draw(bk)
    draw.line([(0,HEIGHT_6IN/2),(WIDTH_6IN,HEIGHT_6IN/2)],fill=128) # 横线
    draw.line([(WIDTH_6IN*0.25,0),(WIDTH_6IN*0.25,HEIGHT_6IN)],fill=128) # 第1条竖线
    draw.line([(WIDTH_6IN*0.5,0),(WIDTH_6IN*0.5,HEIGHT_6IN)],fill=128) # 第2条竖线
    draw.line([(WIDTH_6IN*0.75,0),(WIDTH_6IN*0.75,HEIGHT_6IN)],fill=128) # 第3条竖线
    focus_point = [0.125 * WIDTH_6IN,0.25 * HEIGHT_6IN]
    start_point = [focus_point[0] - 0.5 * WIDTH_2IN, focus_point[1] - 0.5 * HEIGHT_2IN]
    for i in range(0,2):
        for k in range(0,4):
            bk.paste(photo, (int(start_point[0] + (k * WIDTH_6IN / 4)), int(start_point[1] + 0.5 * i * HEIGHT_6IN)))
    return bk


def layout_photo_6_mix1(photo1,photo2):
    """
    在6寸照片上混合排版1寸、2寸照片
    :param photo1: 待处理照片1寸
    :param photo1: 待处理照片2寸
    :return: 处理后的照片
    """
    bk = Image.new("RGB", [WIDTH_6IN,HEIGHT_6IN], (255,255,255))
    # 创建画笔
    draw = ImageDraw.Draw(bk)
    draw.line([(0,HEIGHT_6IN*0.5),(WIDTH_6IN,HEIGHT_6IN/2)],fill=128) # 横线
    draw.line([(0,HEIGHT_6IN*0.25),(WIDTH_6IN*0.5,HEIGHT_6IN*0.25)],fill=128) # 短横线
    draw.line([(0,HEIGHT_6IN*0.75),(WIDTH_6IN*0.5,HEIGHT_6IN*0.75)],fill=128) # 短横线
    draw.line([(WIDTH_6IN*0.25,0),(WIDTH_6IN*0.25,HEIGHT_6IN)],fill=128) # 第1条竖线
    draw.line([(WIDTH_6IN*0.5,0),(WIDTH_6IN*0.5,HEIGHT_6IN)],fill=128) # 第2条竖线
    draw.line([(WIDTH_6IN*0.75,0),(WIDTH_6IN*0.75,HEIGHT_6IN)],fill=128) # 第3条竖线
    focus_point = [0.125 * WIDTH_6IN, 0.125 * HEIGHT_6IN]
    start_point = [focus_point[0] - 0.5 * HEIGHT_1IN, focus_point[1] - 0.5 * WIDTH_1IN]
    for i in range(0,4):
        for k in range(0,2):
            bk.paste(photo1, (int(start_point[0] + (0.25 * k * WIDTH_6IN )), int(start_point[1] + 0.25 * i * HEIGHT_6IN)))
    focus_point2 = [0.625 * WIDTH_6IN, 0.25 * HEIGHT_6IN]
    start_point2 = [focus_point2[0] - 0.5 * WIDTH_2IN, focus_point2[1] - 0.5 * HEIGHT_2IN]
    for i in range(0,2):
        for k in range(0,2):
            bk.paste(photo2,(int(start_point2[0] + (0.25 * k * WIDTH_6IN)), int(start_point2[1] + 0.5 * i * HEIGHT_6IN)))
    bk.show()
    return bk



def layout_photo_6_mix2(photo1,photo2):
    """
    在6寸照片上混合排版1寸、2寸照片
    :param photo1: 待处理照片1寸
    :param photo1: 待处理照片2寸
    :return: 处理后的照片
    """
    bk = Image.new("RGB", [HEIGHT_6IN,WIDTH_6IN], (255,255,255)) # 竖版排版
    # 创建画笔
    draw = ImageDraw.Draw(bk)

    draw.line([(350,0),(350,WIDTH_6IN)],fill=128) # 竖线
    draw.line([(700,0),(700,WIDTH_6IN)],fill=128) # 竖线


    draw.line([(0,WIDTH_6IN*0.25),(700,WIDTH_6IN*0.25)],fill=128) # 横线1
    draw.line([(0,WIDTH_6IN*0.5),(700,WIDTH_6IN*0.5)],fill=128) # 横线2
    draw.line([(0,WIDTH_6IN*0.75),(700,WIDTH_6IN*0.75)],fill=128) # 横线3
    draw.line([(700,WIDTH_6IN/3),(HEIGHT_6IN,WIDTH_6IN/3)],fill=128) # 横线4
    draw.line([(700,WIDTH_6IN*2/3),(HEIGHT_6IN,WIDTH_6IN*2/3)],fill=128) # 横线5

    focus_point = [0.5 * 350, 0.125 * WIDTH_6IN]
    start_point = [focus_point[0] - 0.5 * WIDTH_1IN, focus_point[1] - 0.5 * HEIGHT_1IN]

    #print(focus_point,start_point)
    for i in range(0,4):
        for k in range(0,2):
            bk.paste(photo1, (int(start_point[0] + (k * 350)), int(start_point[1] + i * 0.25 * WIDTH_6IN )))

    focus_point2 = [0.5 * HEIGHT_6IN+350,  WIDTH_6IN/6]
    start_point2 = [focus_point2[0] - 0.5 * WIDTH_2IN, focus_point2[1] - 0.5 * HEIGHT_2IN]
    for i in range(0,3):
        bk.paste(photo2, (int(start_point2[0]), int(start_point2[1] + i  * WIDTH_6IN /3)))
    return bk

def 排版(img,path):


    layout_photo_6_mix2(resize_photo(cut_photo(img,1),1),resize_photo(cut_photo(img,2),2)).save(path, format='JPEG')

#====================================================================================================================================================

#====================================================================================================================================================
#====================================================================================================================================================
#====================================================================================================================================================
#====================================================================================================================================================
#====================================================================================================================================================
#====================================================================================================================================================
#====================================================================================================================================================



        
def sfz(file, side='人像页'):
    from io import BytesIO
    try:
        # 读取文件内容（支持内存文件和路径）
        if isinstance(file, (str, os.PathLike)):
            with open(file, 'rb') as f:
                img = f.read()
        else:
            file.seek(0)  # 重置文件指针
            img = file.read()
        
        # 添加文件头验证
        if img[0:3] == b'\xFF\xD8\xFF':
            format = 'JPEG'
        elif img[0:8] == b'\x89PNG\r\n\x1a\n':
            format = 'PNG'
        elif img[0:6] in (b'GIF87a', b'GIF89a'):
            format = 'GIF'
        else:
            raise ValueError("不支持的图片格式")

        # 使用更健壮的图片处理方式
        with Image.open(BytesIO(img)) as im:
            im.draft(im.mode, (1024, 1024))  # 限制分辨率
            if im.mode != 'RGB':
                im = im.convert('RGB')
            
            output_buffer = BytesIO()
            im.save(output_buffer, format=format, quality=85)
            img = output_buffer.getvalue()

        # ... 原有OCR处理代码保持不变 ...
        
    except Exception as e:
        print(f"图片处理失败: {e} | 文件大小: {len(img)}字节 | 文件头: {img[:8].hex()}")
        return "未知姓名", "未知号码"
  
      
        
    # 读取图片

    idCardSide = {'人像页':'front','国徳页':'back'}.get(side,'front')  # 身份证正面
    # idCardSide = 'back'   #身份证反面

    options = {}
    options['detect_direction'] = 'true'  # 是否检测图像朝向，默认不检测
    options['detect_risk'] = 'false'  # 是否开启身份证风险类型

    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    text = client.idcard(img, idCardSide, options)


    concat_text = {}
    if isinstance(text, dict):
        words = text['words_result']

        name = False
        id = False

        for k, v in words.items():

            if '姓名' in k:

                dic = {k: v['words']}

                concat_text.update(dic)
                name = concat_text['姓名']

            elif '号码' in k:
                dic = {k: v['words']}
                concat_text.update(dic)

                id = concat_text['公民身份号码']

        return name, str(id)







# A4纸尺寸（300dpi分辨率）
a4_width = 2480
a4_height = 3508
spacing = 236  # 2cm转换为像素（300dpi时）

def combine_a4_images(img1, img2):
    # 创建白色A4背景
    background = Image.new('RGB', (a4_width, a4_height), (255, 255, 255))
    
    # 计算图片位置
    total_height = img1.height + spacing + img2.height
    start_y = (a4_height - total_height) // 2
    
    # 居中粘贴第一张图
    x_center = (a4_width - img1.width) // 2
    background.paste(img1, (x_center, start_y))
    
    # 粘贴第二张图
    second_y = start_y + img1.height + spacing
    background.paste(img2, (x_center, second_y))
    
    return background







