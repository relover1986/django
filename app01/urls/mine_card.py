from django.urls import path
from app01 import views

urlpatterns = [
    path("home/mine_card/", views.mine_card_index, name="mine_card_index"),
    path("home/mine_card/delete/<int:worker_id>/", views.mine_card_delete, name="mine_card_delete"),
    path("home/mine_card/batch_delete/", views.mine_card_batch_delete, name="mine_card_batch_delete"),
    path("home/mine_card/photo/<int:worker_id>/", views.mine_card_update_photo, name="mine_card_update_photo"),
    path("home/mine_card/preview/", views.mine_card_preview, name="mine_card_preview"),
    path("home/mine_card/download/", views.mine_card_download, name="mine_card_download"),
]
