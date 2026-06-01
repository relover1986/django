from django.urls import path
from app01 import login
from app01 import staff_login

urlpatterns = [
    path("login/", login.login, name="login"),
    path("logout/", login.logout, name="logout"),
    path("staff_login/", staff_login.staff_login, name="staff_login"),
]
