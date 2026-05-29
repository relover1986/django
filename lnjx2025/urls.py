"""
URL configuration for lnjx2025 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from app01 import views
from django.urls import re_path
from django.views.static import serve
import os

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



from app01 import change
from app01 import quiz
from app01 import grades

from app01 import login
from app01.views import StaffListView
from app01.views_staff import (
    staff_list, staff_add, staff_edit, staff_detail, staff_delete,
    staff_cert_add, staff_cert_delete, staff_cert_file_add, staff_cert_list,
    staff_cert_export_zip,
    cert_type_list, cert_type_add, cert_type_edit, cert_type_delete,
)

urlpatterns = [
    #path("admin/", admin.site.urls),

    # Root path redirect to login
    path("", lambda request: redirect("/login/")),

    # path("staff_list/", views.staff_list),



        re_path(r'^.well-known/acme-challenge/(?P<path>.*)$', serve, {
        'document_root': os.path.join(BASE_DIR, '.well-known/acme-challenge'),
    }),

    path("home/admin_add/", views.admin_add),
    path("home/admin_edit/", views.admin_edit),
    path("home/admin_delete/", views.admin_delete),
    path("staff_edit/", views.admin_edit),  # 已废弃，保留兼容
    path('home/admin/', StaffListView.as_view(template_name='staff_list_v2.html'), name='staff_list'),
    # path("staff_edit_handle/", views.staff_edit_handle),
    # path("staff_search/", views.staff_search),

    # 人员管理（新）
    path("home/staff/", staff_list, name="staff_list_new"),
    path("home/staff/add/", staff_add, name="staff_add"),
    path("home/staff/<int:pk>/edit/", staff_edit, name="staff_edit"),
    path("home/staff/<int:pk>/", staff_detail, name="staff_detail"),
    path("home/staff/<int:pk>/delete/", staff_delete, name="staff_delete"),
    path("home/staff/<int:pk>/cert/add/", staff_cert_add, name="staff_cert_add"),
    path("home/staff_cert/<int:pk>/delete/", staff_cert_delete, name="staff_cert_delete"),
    path("home/staff_cert/<int:pk>/file/add/", staff_cert_file_add, name="staff_cert_file_add"),

    # 证件类型管理
    path("cert-type/", cert_type_list, name="cert_type_list"),
    path("cert-type/add/", cert_type_add, name="cert_type_add"),
    path("cert-type/<int:pk>/edit/", cert_type_edit, name="cert_type_edit"),
    path("cert-type/<int:pk>/delete/", cert_type_delete, name="cert_type_delete"),
    path("home/staff_cert/", staff_cert_list, name="staff_cert_list"),
    path("home/staff_cert/export/zip/", staff_cert_export_zip, name="staff_cert_export_zip"),


    path('upload/', views.upload_model),


    path('home/contractlabor_add/', views.contractlabor_add),
    path('home/contractlabor_delete/', views.contractlabor_delete),
    path('home/contractlabor_list/', views.contractlabor_list),
    path('home/contractlabor_export_zip/', views.contractlabor_export_zip, name='labor_export'),

    # 入井证
    path('home/mine_card/', views.mine_card_index, name='mine_card_index'),
    path('home/mine_card/delete/<int:worker_id>/', views.mine_card_delete, name='mine_card_delete'),
    path('home/mine_card/photo/<int:worker_id>/', views.mine_card_update_photo, name='mine_card_update_photo'),
    path('home/mine_card/preview/', views.mine_card_preview, name='mine_card_preview'),
    path('home/mine_card/download/', views.mine_card_download, name='mine_card_download'),

    # 新增求职者档案路由
    path('home/candidateprofile_add/', views.candidateprofile_add),
    path('home/candidateprofile_delete/', views.candidateprofile_delete),
    path('home/candidateprofile_list/', views.candidateprofile_list),




    path('home/weighingrecord_add/', views.weighingrecord_add),
    path('home/weighingrecord_delete/', views.weighingrecord_delete),
    path('home/weighingrecord_list/', views.weighingrecord_list),




    path('home/photo_add/', views.photo_add),
    path('home/photo_delete/', views.photo_delete),

    # 爆破现场记录
    path('home/blasting_site_photo_add/', views.blasting_site_photo_add),
    path('home/blasting_site_photo_delete/', views.blasting_site_photo_delete),
    path('home/blasting_site_photo_list/', views.blasting_site_photo_list),
    path('home/blasting_site_low_conf/', views.blasting_site_low_conf),
    path('home/blasting_site_low_conf_delete/', views.blasting_site_low_conf_delete),
    path('home/blasting_site_low_conf_submit/', views.blasting_site_low_conf_submit),
    path('home/blasting_site_train_signatures/', views.blasting_site_train_signatures),
    path('home/photo_list/', views.photo_list),
    path('home/generate_white_bg/', views.generate_white_bg),
    path('home/photo_export_zip/', views.photo_export_zip, name='photo_export_zip'),


    # 照片管理API接口
    path('api/photo/upload/', views.PhotoUploadAPIView.as_view(),
         name='api_photo_upload'),
    path('api/photo/list/', views.PhotoListAPIView.as_view(),
         name='api_photo_list'),
    path('api/photo/detail/<int:photo_id>/', views.PhotoDetailAPIView.as_view(),
         name='api_photo_detail'),
    path('api/photo/delete/<int:photo_id>/', views.PhotoDeleteAPIView.as_view(),
         name='api_photo_delete'),



    # 爆破证书管理(统一为home前缀)
    path('home/blastingcertificate_add/', views.blastingcertificate_add, name='blastingcertificate_add'),
    path('home/blastingcertificate_delete/', views.blastingcertificate_delete, name='blastingcertificate_delete'),
    path('home/blastingcertificate_list/', views.blastingcertificate_list, name='blastingcertificate_list'),
    path('home/blastingcertificate_export_zip/', views.blastingcertificate_export_zip, name='blastingcertificate_export_zip'),
    path('home/blastingcertificate_export_xlsx/', views.blastingcertificate_export_xlsx, name='blastingcertificate_export_xlsx'),

    # 爆破作业登记

    # 作业点
    # 爆破员列表
    path('home/blaster_list/', views.blaster_list, name='blaster_list'),
    path('home/blaster_add/', views.blaster_add, name='blaster_add'),
    path('home/blasting_summary_list/', views.blasting_summary_list, name='blasting_summary_list'),
    path('home/blasting_summary_add/', views.blasting_summary_add, name='blasting_summary_add'),
    path('home/blasting_summary_delete/<int:pk>/', views.blasting_summary_delete, name='blasting_summary_delete'),
    path('home/blasting_summary_assign_blaster/', views.blasting_summary_assign_blaster, name='blasting_summary_assign_blaster'),
    path('home/blasting_stats/', views.blasting_stats, name='blasting_stats'),

    path('home/idcard_add/', views.idcard_add),
    path('home/idcard_delete/', views.idcard_delete),
    path('home/idcard_list/', views.idcard_list),
    path('home/idcard_batch_upload/', views.idcard_batch_upload),
    path('home/idcard_export_zip/', views.idcard_export_zip, name='idcard_export_zip'),

    path('home/explosivestaff_add/', views.explosivestaff_add),
    path('home/explosivestaff_delete/', views.explosivestaff_delete),
    path('home/explosivestaff_list/', views.explosivestaff_list),
    path('home/explosivestaff_export_zip/', views.explosivestaff_export_zip, name='export_zip'),
    path('home/explosivestaff_export_xlsx/', views.explosivestaff_export_xlsx, name='export_xlsx'),







    path('home/pdf_add/', views.pdf_add),
    path('home/pdf_delete/', views.pdf_delete),
    path('home/pdf_list/', views.pdf_list),







    path('home/tu_add/', views.tu_add),
    path('home/tu_delete/', views.tu_delete),
    path('home/tu_list/', views.tu_list),



    path("login/", login.login),
    # path("register/", views.register),
    path("logout/", login.logout),
    path("home/", views.home),

    path('home/baopo_ti_new_reload', quiz.ti_new_reload),
    path('home/baopo_ti_new', quiz.ti_new),
    path('home/ti_grades', change.grades),
    path('home/grades_new', grades.grades_new),
    path('home/ti_reload', change.questions_reload),



    path('home/jskjgti_grades', change.grades),
    path('home/jskjgti_reload', change.jskjgquestions_reload),
    path('home/jskjgti_new_reload', quiz.jskjgti_new_reload),
    path('home/jskjgti_new', quiz.jskjgti_new),


    path('home/wxpzxti_grades', change.grades),
    path('home/wxpzxti_reload', change.wxpzxquestions_reload),
    path('home/wxpzxti_new_reload', quiz.wxpzxti_new_reload),
    path('home/wxpzxti_new', quiz.wxpzxti_new),


    










    path('home/inventory_list', views.inventory_list),
    path('home/inventory_add', views.inventory_add),
    path('home/inventory_delete', views.inventory_delete),
    path('home/inventory_edit', views.inventory_edit),  #
    path('home/inventory_export_xlsx/', views.inventory_export_xlsx, name='export_xlsx'),










    path('home/categorycontent_list', views.categorycontent_list),
    path('home/categorycontent_create', views.categorycontent_create),
    path('home/categorycontent_delete', views.categorycontent_delete),
    path('home/categorycontent_edit', views.categorycontent_edit),

    path('api/', include('app01.api_urls')),
    path('',include('app01.urls')),




] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# 添加媒体文件URL配置(仅在开发环境使用)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# PWA
from app01.pwa_views import manifest_json, service_worker, push_subscribe, push_unsubscribe, push_public_key

urlpatterns += [
    path('manifest.json', manifest_json, name='manifest_json'),
    path('sw.js', service_worker, name='service_worker'),
    path('api/push/subscribe/', push_subscribe, name='push_subscribe'),
    path('api/push/unsubscribe/', push_unsubscribe, name='push_unsubscribe'),
    path('api/push/public-key/', push_public_key, name='push_public_key'),
]
