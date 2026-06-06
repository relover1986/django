from django.urls import path
from app01 import quiz

urlpatterns = [
    path("home/custom_quiz", quiz.custom_quiz),
    path("home/custom_quiz_reload", quiz.custom_quiz_reload),
    path("home/download_example_questions", quiz.download_example_questions),
    path("home/import_questions", quiz.import_questions),
    path("home/export_quiz", quiz.export_docx),
]
