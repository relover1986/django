from django.urls import path
from app01.views.info_collect import info_collect, info_collect_success

urlpatterns = [
    path('home/info_collect/', info_collect, name='info_collect'),
    path('home/info_collect/success/', info_collect_success, name='info_collect_success'),
]
