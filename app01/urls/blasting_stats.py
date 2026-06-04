from django.urls import path
from app01 import views

urlpatterns = [
    path("home/blasting_summary_list/", views.blasting_summary_list, name="blasting_summary_list"),
    path("home/blasting_summary_add/", views.blasting_summary_add, name="blasting_summary_add"),
    path("home/blasting_summary_delete/<int:pk>/", views.blasting_summary_delete, name="blasting_summary_delete"),
    path("home/blasting_summary_assign_blaster/", views.blasting_summary_assign_blaster, name="blasting_summary_assign_blaster"),
    path("home/blasting_stats/", views.blasting_stats, name="blasting_stats"),
]
