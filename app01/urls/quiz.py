from django.urls import path
from app01.views import change
from app01 import quiz
from app01.views import grades

urlpatterns = [
    path("home/baopo_ti_new_reload", quiz.ti_new_reload),
    path("home/baopo_ti_new", quiz.ti_new),
    path("home/ti_grades", change.grades),
    path("home/grades_new", grades.grades_new),
    path("home/ti_reload", change.questions_reload),
    path("home/jskjgti_grades", change.grades),
    path("home/jskjgti_reload", change.jskjgquestions_reload),
    path("home/jskjgti_new_reload", quiz.jskjgti_new_reload),
    path("home/jskjgti_new", quiz.jskjgti_new),
    path("home/wxpzxti_grades", change.grades),
    path("home/wxpzxti_reload", change.wxpzxquestions_reload),
    path("home/wxpzxti_new_reload", quiz.wxpzxti_new_reload),
    path("home/wxpzxti_new", quiz.wxpzxti_new),
    path("home/custom_quiz", quiz.custom_quiz),
    path("home/custom_quiz_reload", quiz.custom_quiz_reload),
    path("home/download_example_questions", quiz.download_example_questions),
    path("home/import_questions", quiz.import_questions),
    path("home/export_quiz", quiz.export_docx),
]
