from django.urls import path
from app01 import views

urlpatterns = [
    path("home/photo_add/", views.photo_add),
    path("home/photo_delete/", views.photo_delete),
    path("home/photo_batch_delete/", views.photo_batch_delete),
    path("home/photo_list/", views.photo_list),
    path("home/generate_white_bg/", views.generate_white_bg),
    path("home/photo_export_zip/", views.photo_export_zip, name="photo_export_zip"),
    path("api/photo/upload/", views.PhotoUploadAPIView.as_view(), name="api_photo_upload"),
    path("api/photo/list/", views.PhotoListAPIView.as_view(), name="api_photo_list"),
    path("api/photo/detail/<int:photo_id>/", views.PhotoDetailAPIView.as_view(), name="api_photo_detail"),
    path("api/photo/delete/<int:photo_id>/", views.PhotoDeleteAPIView.as_view(), name="api_photo_delete"),
]
