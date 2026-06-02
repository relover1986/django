from django.urls import path
from . import views

urlpatterns = [
    # API 路由已在主 urls.py 中配置
    path('home/test_upload/', views.test_upload, name='test_upload'),
]