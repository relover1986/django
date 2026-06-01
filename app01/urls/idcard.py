from django.urls import path
from app01 import views

urlpatterns = [
    path("home/idcard_add/", views.idcard_add),
    path("home/idcard_delete/", views.idcard_delete),
    path("home/idcard_list/", views.idcard_list),
    path("home/idcard_batch_upload/", views.idcard_batch_upload),
    path("home/idcard_export_zip/", views.idcard_export_zip, name="idcard_export_zip"),
]
