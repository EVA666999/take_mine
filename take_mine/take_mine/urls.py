from django.contrib import admin
from django.urls import path, include
from api.urls import router

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("app.urls")),
    path('users/', include('users.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api-v1/', include(router.urls)),
    path('api-v1/', include('auth.urls')),
    
]