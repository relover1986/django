# 架构图 — 直接用固定文件 serve
from django.http import FileResponse
import os

def architecture_diagram_view(request):
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "architecture_diagram.html")
    return FileResponse(open(path, "rb"), content_type="text/html")
# 企业督办看板 — test 页面
def kanban_view(request):
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kanban.html")
    return FileResponse(open(path, "rb"), content_type="text/html")

# 矿山安全生产数字化管理清单
def mine_safety_checklist_view(request):
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'mine_safety_checklist.html')
    return FileResponse(open(path, 'rb'), content_type='text/html')
# 装药结构示意图工具
def zhuangyao_structure_view(request):
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "装药结构图工具.html")
    return FileResponse(open(path, "rb"), content_type="text/html")
