from django.shortcuts import render
from rest_framework import filters, viewsets
from app.models import Category, Item, ExchangeProposal
from .serializers import CategorySerializer, ItemSerializer, ExchangeProposalSerializer
from rest_framework.permissions import IsAdminUser
from rest_framework import viewsets, serializers, permissions
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
class ExchangeProposalViewSet(viewsets.ModelViewSet):
    queryset = ExchangeProposal.objects.all()
    serializer_class = ExchangeProposalSerializer