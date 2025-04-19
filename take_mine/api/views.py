from django.shortcuts import render
from rest_framework import filters, viewsets
from app.models import Category, Item, ExchangeProposal
from .paginator import CustomLimitOffsetPagination
from .serializers import CategorySerializer, ItemSerializer, ExchangeProposalSerializer, MyProposalsSerializer
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, serializers, permissions
from .permissions import IsAuthorOrAdminOrReadOnly, IsAdmin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from app.models import ExchangeProposal
from django.db.models import Q
from django.shortcuts import get_object_or_404
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
    pagination_class = CustomLimitOffsetPagination

    def perform_create(self, serializer):
        
        ad_receiver = serializer.validated_data.get('ad_receiver')
        if ad_receiver.user == self.request.user:
            raise serializers.ValidationError(
                "Нельзя предлагать обмен на свой собственный товар"
            )
        ExchangeProposal.objects.filter(
            ad_receiver=ad_receiver, 
            status__in=['ожидает', 'принята']
        ).update(status='забрали')
        
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
        ).order_by('-created_at')
    
class AcceptProposalView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        proposal = get_object_or_404(ExchangeProposal, pk=pk)
        if proposal.status != 'ожидает':
            return Response({'error': 'Предложение уже обработано'}, status=status.HTTP_400_BAD_REQUEST)
        if proposal.ad_receiver.user != request.user:
            return Response({'error': 'Вы не можете принять это предложение'}, status=status.HTTP_403_FORBIDDEN)
        proposal.status = 'принята'
        proposal.save()
        return Response({'status': 'Предложение принято'})

class RejectProposalView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        proposal = get_object_or_404(ExchangeProposal, pk=pk)
        if proposal.status != 'ожидает':
            return Response({'error': 'Предложение уже обработано'}, status=status.HTTP_400_BAD_REQUEST)
        if proposal.ad_receiver.user != request.user:
            return Response({'error': 'Вы не можете отклонить это предложение'}, status=status.HTTP_403_FORBIDDEN)
        proposal.status = 'отклонена'
        proposal.save()
        return Response({'status': 'Предложение отклонено'})
    
