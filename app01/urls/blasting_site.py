from django.urls import path
from app01 import views

urlpatterns = [
    path("home/blasting_site_photo_add/", views.blasting_site_photo_add),
    path("home/blasting_site_photo_delete/", views.blasting_site_photo_delete),
    path("home/blasting_site_photo_list/", views.blasting_site_photo_list),
    path("home/blasting_site_low_conf/", views.blasting_site_low_conf),
    path("home/blasting_site_low_conf_delete/", views.blasting_site_low_conf_delete),
    path("home/blasting_site_low_conf_submit/", views.blasting_site_low_conf_submit),
    path("home/blasting_site_train_signatures/", views.blasting_site_train_signatures),
]
