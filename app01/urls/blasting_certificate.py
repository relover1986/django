from django.urls import path
from app01 import views

urlpatterns = [
    path("home/blastingcertificate_add/", views.blastingcertificate_add, name="blastingcertificate_add"),
    path("home/blastingcertificate_delete/", views.blastingcertificate_delete, name="blastingcertificate_delete"),
    path("home/blastingcertificate_list/", views.blastingcertificate_list, name="blastingcertificate_list"),
    path("home/blastingcertificate_export_zip/", views.blastingcertificate_export_zip, name="blastingcertificate_export_zip"),
    path("home/blastingcertificate_export_xlsx/", views.blastingcertificate_export_xlsx, name="blastingcertificate_export_xlsx"),
]
