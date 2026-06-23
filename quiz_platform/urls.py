from django.urls import path
from . import views

app_name = "quiz_platform"

urlpatterns = [
    path("", views.index, name="index"),
    path("round/", views.start_round, name="start-round"),
    path("submit/", views.submit_round, name="submit-round"),
    path("wrong-book/", views.wrong_book, name="wrong-book"),
    path("update-chapter/", views.update_chapter, name="update-chapter"),
    path("reset/", views.reset_question, name="reset-question"),
    path("stats/", views.stats, name="stats"),
    path("qa/", views.qa_page, name="qa-page"),
    path("qa/ask/", views.qa_ask, name="qa-ask"),
]
