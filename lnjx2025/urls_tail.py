# 架构图 — 直接用固定文件 serve
from django.http import FileResponse
import os

def architecture_diagram_view(request):
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "architecture_diagram.html")
    return FileResponse(open(path, "rb"), content_type="text/html")
