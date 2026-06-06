from django.urls import path
from app01 import views

urlpatterns = [
    path("home/", views.home, name="home"),
    path("home/department_quiz_stats/", views.department_quiz_stats, name="department_quiz_stats"),
    # Vue 前端
    path("vue/", views.vue_app),
    path("vue/<path:vue_path>/", views.vue_app),
]
