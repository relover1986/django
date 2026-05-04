import requests
from io import BytesIO
from PIL import Image

def test_photo_upload():
    # 创建一个测试图片
    img = Image.new('RGB', (100, 100), color='red')
    img_io = BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    
    # 测试单个文件上传
    print("测试单个文件上传...")
    files = {'file': ('test.jpg', img_io, 'image/jpeg')}
    r = requests.post('http://localhost:8001/api/photo/upload/', files=files)
    print(f"状态码: {r.status_code}")
    print(f"响应内容: {r.text}")
    print()
    
    # 测试带自定义文件名的上传
    print("测试带自定义文件名的上传...")
    files = {'file': ('custom_name.jpg', img_io, 'image/jpeg')}
    data = {'model_name': '自定义姓名'}
    r = requests.post('http://localhost:8001/api/photo/upload/', files=files, data=data)
    print(f"状态码: {r.status_code}")
    print(f"响应内容: {r.text}")
    print()
    
    # 测试多文件上传
    print("测试多文件上传...")
    img2 = Image.new('RGB', (100, 100), color='blue')
    img2_io = BytesIO()
    img2.save(img2_io, 'JPEG')
    img2_io.seek(0)
    
    files = [
        ('file', ('test1.jpg', img_io, 'image/jpeg')),
        ('file', ('test2.jpg', img2_io, 'image/jpeg'))
    ]
    r = requests.post('http://localhost:8001/api/photo/upload/', files=files)
    print(f"状态码: {r.status_code}")
    print(f"响应内容: {r.text}")

if __name__ == '__main__':
    test_photo_upload()