from django.shortcuts import render
from rest_framework import filters, viewsets
from app.models import Category, Item, ExchangeProposal
from .serializers import CategorySerializer, ItemSerializer, ExchangeProposalSerializer
from rest_framework.permissions import IsAdminUser
from rest_framework import viewsets, serializers, permissions
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
class ExchangeProposalViewSet(viewsets.ModelViewSet):
    queryset = ExchangeProposal.objects.all()
    serializer_class = ExchangeProposalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        
        ad_receiver = serializer.validated_data.get('ad_receiver')
        if ad_receiver.user == self.request.user:
            raise serializers.ValidationError(
                "Нельзя предлагать обмен на свой собственный товар"
            )
        
        serializer.save()