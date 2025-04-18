from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('category/create/', views.create_category, name='create_category'),
    path('item/create/', views.item_create, name='item_create'),
    path('item/<int:item_id>/edit/', views.item_edit, name='item_edit'),
    path('item/<int:item_id>/delete/', views.item_delete, name='item_delete'),
    path('item/<int:item_id>/', views.create_exchange_proposal, name='exchange_proposal'),
    path('exchanges/', views.exchanges_list, name='exchanges'),
    path('exchanges/<int:proposal_id>/accept/', views.accept_exchange, name='accept_exchange'),
    path('exchanges/<int:proposal_id>/reject/', views.reject_exchange, name='reject_exchange'),
    
]