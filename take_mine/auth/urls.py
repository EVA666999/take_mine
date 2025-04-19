from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('create/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
]