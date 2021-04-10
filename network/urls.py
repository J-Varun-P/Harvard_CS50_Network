
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("users/<str:name>", views.users, name="users"),

    # API Routes
    path("addpost", views.addpost, name="addpost"),
    path("editpost", views.editpost, name="editpost"),
    path("likepost", views.likepost, name="likepost"),
    path("unlikepost", views.unlikepost, name="unlikepost"),
]
