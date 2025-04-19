from django.urls import path
from . import views

urlpatterns = [
    path('items/create/', views.item_create, name='item_create'),
    path('items/<int:item_id>/update/', views.item_create, name='item_update'),
    path('items/<int:item_id>/delete/', views.item_delete, name='item_delete'),
    
    
    path('exchange/<int:item_id>/', views.create_exchange_proposal, name='create_exchange_proposal'),
    path('my-proposals/<int:proposal_id>/accept/', views.accept_proposal, name='accept_proposal'),
    path('my-proposals/<int:proposal_id>/reject/', views.reject_proposal, name='reject_proposal'),
]