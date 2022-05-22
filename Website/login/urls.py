from django.urls import path

from . import views

urlpatterns = [
    path("", views.base, name="base"),
    path("user_login/", views.user_login, name="user_login"),
    path("create_account/", views.create_account, name="create_account"),
    path("changePassword/", views.changePassword, name="changePassword"),
]
