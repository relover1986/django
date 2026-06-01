from django.urls import path
from app01 import views

urlpatterns = [
    path("home/explosivestaff_add/", views.explosivestaff_add),
    path("home/explosivestaff_delete/", views.explosivestaff_delete),
    path("home/explosivestaff_list/", views.explosivestaff_list),
    path("home/explosivestaff_export_zip/", views.explosivestaff_export_zip, name="export_zip"),
    path("home/explosivestaff_export_xlsx/", views.explosivestaff_export_xlsx, name="export_xlsx"),
]
