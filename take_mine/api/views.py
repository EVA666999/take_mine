from django.shortcuts import render
from rest_framework import filters, viewsets
from app.models import Category, Item, ExchangeProposal
from .serializers import CategorySerializer, ItemSerializer, ExchangeProposalSerializer, MyProposalsSerializer
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, serializers, permissions
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter]
    
    filterset_fields = ['category__name', 'condition']
    
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']

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

class MyProposalsViewSet(viewsets.ModelViewSet):
    serializer_class = MyProposalsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter, 
        filters.OrderingFilter
    ]
    filterset_fields = ['status']
    search_fields = ['comment']
    ordering_fields = ['created_at', 'status']

    def get_queryset(self):
        user = self.request.user
        return ExchangeProposal.objects.filter(ad_sender__user=user)