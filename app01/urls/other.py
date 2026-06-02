from django.urls import path
from app01 import views

urlpatterns = [
    path("upload/", views.upload_model),
    path("home/candidateprofile_add/", views.candidateprofile_add),
    path("home/candidateprofile_delete/", views.candidateprofile_delete),
    path("home/candidateprofile_list/", views.candidateprofile_list),
    path("home/weighingrecord_add/", views.weighingrecord_add),
    path("home/weighingrecord_delete/", views.weighingrecord_delete),
    path("home/weighingrecord_list/", views.weighingrecord_list),
    path("home/pdf_add/", views.pdf_add),
    path("home/pdf_delete/", views.pdf_delete),
    path("home/pdf_list/", views.pdf_list),
    path("home/tu_add/", views.tu_add),
    path("home/tu_delete/", views.tu_delete),
    path("home/tu_list/", views.tu_list),
    path("home/inventory_list", views.inventory_list),
    path("home/inventory_add", views.inventory_add),
    path("home/inventory_delete", views.inventory_delete),
    path("home/inventory_edit", views.inventory_edit),
    path("home/inventory_export_xlsx/", views.inventory_export_xlsx, name="export_xlsx"),
    path("home/categorycontent_list", views.categorycontent_list),
    path("home/categorycontent_create", views.categorycontent_create),
    path("home/categorycontent_delete", views.categorycontent_delete),
    path("home/categorycontent_edit", views.categorycontent_edit),
    path('home/test_upload/', views.test_upload, name='test_upload'),
]
