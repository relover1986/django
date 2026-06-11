from django.urls import path
from app01.views.info_collect import info_collect, info_collect_success, info_submission_edit, info_submissions_list

urlpatterns = [
    path('home/info_collect/', info_collect, name='info_collect'),
    path('home/staff/info_submissions/', info_submissions_list, name='info_submissions_list'),
    path('home/staff/info_submissions/<int:pk>/edit/', info_submission_edit, name='info_submission_edit'),
    path('home/info_collect/success/', info_collect_success, name='info_collect_success'),
]
