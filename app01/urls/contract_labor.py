from django.urls import path
from app01 import views

urlpatterns = [
    path("home/contractlabor_add/", views.contractlabor_add),
    path("home/contractlabor_delete/", views.contractlabor_delete),
    path("home/contractlabor_list/", views.contractlabor_list),
    path("home/contractlabor_export_zip/", views.contractlabor_export_zip, name="labor_export"),
]
