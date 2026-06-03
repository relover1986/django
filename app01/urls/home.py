from django.urls import path
from app01 import views

urlpatterns = [
    path("home/", views.home, name="home"),
]
