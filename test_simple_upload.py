import requests
from io import BytesIO
from PIL import Image
import traceback

def test_simple_upload():
    # 创建一个测试图片
    img = Image.new('RGB', (100, 100), color='red')
    img_io = BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    
    # 测试单个文件上传
    print("测试单个文件上传...")
    try:
        files = {'file': ('test.jpg', img_io, 'image/jpeg')}
        r = requests.post('http://localhost:8001/api/photo/upload/', files=files, timeout=10)
        print(f"状态码: {r.status_code}")
        print(f"响应内容: {r.text}")
    except Exception as e:
        print(f"请求失败: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    test_simple_upload()