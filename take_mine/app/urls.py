from django.urls import path
from . import views

namespace = 'app'

urlpatterns = [
    path('', views.index, name='home'),
    path('category/create/', views.create_category, name='create_category'),
]