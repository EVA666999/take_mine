from django.shortcuts import render, get_object_or_404
from rest_framework import filters, viewsets, status, permissions
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from app.models import Category, Item, ExchangeProposal
from .paginator import CustomLimitOffsetPagination
from .serializers import (
    CategorySerializer, 
    ItemSerializer, 
    ExchangeProposalSerializer, 
    MyProposalsSerializer
)
from .permissions import IsAuthorOrAdminOrReadOnly, IsAdmin


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin]
    pagination_class = CustomLimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination
    
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    
    filterset_fields = ['category__name', 'condition']
    
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MyItemsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Представление для отображения вещей
    """
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination
    
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    
    filterset_fields = ['category__name', 'condition']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']

    def get_queryset(self):
        """
        Возвращает только вещи текущего пользователя
        """
        return Item.objects.filter(user=self.request.user).order_by('-created_at')
        

class ExchangeProposalViewSet(viewsets.ModelViewSet):
    queryset = ExchangeProposal.objects.all()
    serializer_class = ExchangeProposalSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination

    def perform_create(self, serializer):
        ad_sender = serializer.validated_data.get('ad_sender')
        ad_receiver = serializer.validated_data.get('ad_receiver')
        
        # Проверяем, принадлежит ли предмет-отправитель текущему пользователю
        if ad_sender.user != self.request.user:
            raise serializers.ValidationError(
                "Вы можете предлагать обмен только своих предметов"
            )
        
        # Проверяем, не принадлежит ли предмет-получатель текущему пользователю
        if ad_receiver.user == self.request.user:
            raise serializers.ValidationError(
                "Нельзя предлагать обмен на свой собственный товар"
            )
            
        # Создаем предложение обмена
        serializer.save()


class MyProposalsViewSet(viewsets.ModelViewSet):
    serializer_class = MyProposalsSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination
    
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
        return ExchangeProposal.objects.filter(
            Q(ad_sender__user=user) | Q(ad_receiver__user=user)
        ).exclude(
            status='забрали'  # Исключаем предложения со статусом "забрали"
        ).order_by('-created_at')
    

class AcceptProposalView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        proposal = get_object_or_404(ExchangeProposal, pk=pk)
        
        # Проверка статуса предложения
        if proposal.status != 'ожидает':
            return Response(
                {'error': 'Предложение уже обработано'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверка прав пользователя
        if proposal.ad_receiver.user != request.user:
            return Response(
                {'error': 'Вы не можете принять это предложение'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Обмен товарами между пользователями
        sender_item = proposal.ad_sender
        receiver_item = proposal.ad_receiver
        
        # Меняем владельцев товаров
        sender_item.user = proposal.ad_receiver.user
        receiver_item.user = proposal.ad_sender.user
        
        # Сохраняем изменения
        sender_item.save()
        receiver_item.save()
        
        # Закрываем все ожидающие предложения для этих товаров
        ExchangeProposal.objects.filter(
            Q(ad_sender=sender_item) | Q(ad_receiver=sender_item) |
            Q(ad_sender=receiver_item) | Q(ad_receiver=receiver_item),
            status='ожидает'
        ).update(status='забрали')
        
        # Принимаем текущее предложение
        proposal.status = 'принята'
        proposal.save()
        
        return Response({'status': 'Обмен успешно завершен'})


class RejectProposalView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        proposal = get_object_or_404(ExchangeProposal, pk=pk)
        
        if proposal.status != 'ожидает':
            return Response(
                {'error': 'Предложение уже обработано'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if proposal.ad_receiver.user != request.user:
            return Response(
                {'error': 'Вы не можете отклонить это предложение'}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        proposal.status = 'отклонена'
        proposal.save()
        
        return Response({'status': 'Предложение отклонено'})