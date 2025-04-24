from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    # Заменяем стандартный LoginView на кастомный
    path("login/", views.user_login, name="login"),
    # Остальные маршруты без изменений
    path("register/", views.register, name="register"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="users/logout.html"),
        name="logout",
    ),
]