from django.urls import path
from app01 import views
from app01.views import StaffListView
from app01.views_staff import (
    staff_list, staff_add, staff_edit, staff_detail, staff_delete,
    staff_cert_add, staff_cert_delete, staff_cert_file_add, staff_cert_list,
    staff_cert_export_zip,
    cert_type_list, cert_type_add, cert_type_edit, cert_type_delete,
)

urlpatterns = [
    path("home/admin_add/", views.admin_add),
    path("home/admin_edit/", views.admin_edit),
    path("home/admin_delete/", views.admin_delete),
    path("staff_edit/", views.admin_edit),
    path("home/admin/", StaffListView.as_view(template_name="staff_list_v2.html"), name="staff_list"),
    path("home/staff/", staff_list, name="staff_list_new"),
    path("home/staff/add/", staff_add, name="staff_add"),
    path("home/staff/<int:pk>/edit/", staff_edit, name="staff_edit"),
    path("home/staff/<int:pk>/", staff_detail, name="staff_detail"),
    path("home/staff/<int:pk>/delete/", staff_delete, name="staff_delete"),
    path("home/staff/<int:pk>/cert/add/", staff_cert_add, name="staff_cert_add"),
    path("home/staff_cert/<int:pk>/delete/", staff_cert_delete, name="staff_cert_delete"),
    path("home/staff_cert/<int:pk>/file/add/", staff_cert_file_add, name="staff_cert_file_add"),
    path("cert-type/", cert_type_list, name="cert_type_list"),
    path("cert-type/add/", cert_type_add, name="cert_type_add"),
    path("cert-type/<int:pk>/edit/", cert_type_edit, name="cert_type_edit"),
    path("cert-type/<int:pk>/delete/", cert_type_delete, name="cert_type_delete"),
    path("home/staff_cert/", staff_cert_list, name="staff_cert_list"),
    path("home/staff_cert/export/zip/", staff_cert_export_zip, name="staff_cert_export_zip"),
]
