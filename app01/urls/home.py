from django.urls import path
from app01 import views

urlpatterns = [
    path("home/", views.home, name="home"),
    path("home/department_quiz_stats/", views.department_quiz_stats, name="department_quiz_stats"),
]
