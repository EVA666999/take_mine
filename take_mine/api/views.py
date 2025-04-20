from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Category, ExchangeProposal, Item

from .paginator import CustomLimitOffsetPagination
from .permissions import IsAdmin
from .serializers import (
    CategorySerializer,
    ExchangeProposalSerializer,
    ItemSerializer,
    MyProposalsSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin]
    pagination_class = CustomLimitOffsetPagination

    def list(self, request, *args, **kwargs):
        cache_key = "all_categories"
        cached_categories = cache.get(cache_key)

        if cached_categories is None:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response = self.get_paginated_response(serializer.data)
            else:
                serializer = self.get_serializer(queryset, many=True)
                response = Response(serializer.data)

            cache.set(cache_key, response.data, 60 * 15)
            return response

        return Response(cached_categories)


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["category__name", "condition"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "title"]

    def list(self, request, *args, **kwargs):
        cache_key = f"items_list_{request.query_params}"
        cached_items = cache.get(cache_key)

        if cached_items is None:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response = self.get_paginated_response(serializer.data)
            else:
                serializer = self.get_serializer(queryset, many=True)
                response = Response(serializer.data)

            cache.set(cache_key, response.data, 60 * 15)
            return response

        return Response(cached_items)

    def perform_create(self, serializer):
        cache.clear()
        item = serializer.save(user=self.request.user)


class MyItemsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["category__name", "condition"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "title"]

    def get_queryset(self):
        cache_key = f"my_items_{self.request.user.id}"
        cached_queryset = cache.get(cache_key)

        if cached_queryset is None:
            queryset = Item.objects.filter(user=self.request.user).order_by(
                "-created_at"
            )
            cache.set(cache_key, list(queryset), 60 * 15)
            return queryset

        return Item.objects.filter(id__in=[item.id for item in cached_queryset])


class ExchangeProposalViewSet(viewsets.ModelViewSet):
    queryset = ExchangeProposal.objects.all()
    serializer_class = ExchangeProposalSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination

    def list(self, request, *args, **kwargs):
        cache_key = f"exchange_proposals_{request.user.id}"
        cached_proposals = cache.get(cache_key)

        if cached_proposals is None:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response = self.get_paginated_response(serializer.data)
            else:
                serializer = self.get_serializer(queryset, many=True)
                response = Response(serializer.data)

            cache.set(cache_key, response.data, 60 * 15)
            return response

        return Response(cached_proposals)

    def perform_create(self, serializer):
        ad_sender = serializer.validated_data.get("ad_sender")
        ad_receiver = serializer.validated_data.get("ad_receiver")

        if ad_sender.user != self.request.user:
            raise serializers.ValidationError(
                "Вы можете предлагать обмен только своих предметов"
            )

        if ad_receiver.user == self.request.user:
            raise serializers.ValidationError(
                "Нельзя предлагать обмен на свой собственный товар"
            )

        proposal = serializer.save()
        # Инвалидация кэша
        cache.delete_pattern(f"exchange_proposals_{self.request.user.id}")
        cache.delete_pattern(f"exchange_proposals_{ad_receiver.user.id}")


class MyProposalsViewSet(viewsets.ModelViewSet):
    serializer_class = MyProposalsSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status"]
    search_fields = ["comment"]
    ordering_fields = ["created_at", "status"]

    def get_queryset(self):
        cache_key = f"my_proposals_{self.request.user.id}"
        cached_proposals = cache.get(cache_key)

        if cached_proposals is None:
            queryset = (
                ExchangeProposal.objects.filter(
                    Q(ad_sender__user=self.request.user)
                    | Q(ad_receiver__user=self.request.user)
                )
                .exclude(status="забрали")
                .order_by("-created_at")
            )

            cache.set(cache_key, list(queryset), 60 * 15)
            return queryset

        return ExchangeProposal.objects.filter(
            id__in=[proposal.id for proposal in cached_proposals]
        )


class AcceptProposalView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        cache_key = f"proposal_accept_{pk}"
        cached_result = cache.get(cache_key)

        if cached_result:
            return Response(cached_result)

        proposal = get_object_or_404(ExchangeProposal, pk=pk)

        if proposal.status != "ожидает":
            error_response = {"error": "Предложение уже обработано"}
            cache.set(cache_key, error_response, 60 * 15)
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

        if proposal.ad_receiver.user != request.user:
            error_response = {"error": "Вы не можете принять это предложение"}
            cache.set(cache_key, error_response, 60 * 15)
            return Response(error_response, status=status.HTTP_403_FORBIDDEN)

        sender_item = proposal.ad_sender
        receiver_item = proposal.ad_receiver

        sender_item.user = proposal.ad_receiver.user
        receiver_item.user = proposal.ad_sender.user

        sender_item.save()
        receiver_item.save()

        ExchangeProposal.objects.filter(
            Q(ad_sender=sender_item)
            | Q(ad_receiver=sender_item)
            | Q(ad_sender=receiver_item)
            | Q(ad_receiver=receiver_item),
            status="ожидает",
        ).update(status="забрали")

        proposal.status = "принята"
        proposal.save()

        response_data = {"status": "Обмен успешно завершен"}
        cache.set(cache_key, response_data, 60 * 15)

        # Инвалидация связанных кэшей
        cache.delete_pattern(f"my_proposals_{sender_item.user.id}")
        cache.delete_pattern(f"my_proposals_{receiver_item.user.id}")

        return Response(response_data)


class RejectProposalView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        cache_key = f"proposal_reject_{pk}"
        cached_result = cache.get(cache_key)

        if cached_result:
            return Response(cached_result)

        proposal = get_object_or_404(ExchangeProposal, pk=pk)

        if proposal.status != "ожидает":
            error_response = {"error": "Предложение уже обработано"}
            cache.set(cache_key, error_response, 60 * 15)
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

        if proposal.ad_receiver.user != request.user:
            error_response = {"error": "Вы не можете отклонить это предложение"}
            cache.set(cache_key, error_response, 60 * 15)
            return Response(error_response, status=status.HTTP_403_FORBIDDEN)

        proposal.status = "отклонена"
        proposal.save()

        response_data = {"status": "Предложение отклонено"}
        cache.set(cache_key, response_data, 60 * 15)

        # Инвалидация связанных кэшей
        cache.delete_pattern(f"my_proposals_{proposal.ad_sender.user.id}")
        cache.delete_pattern(f"my_proposals_{proposal.ad_receiver.user.id}")

        return Response(response_data)
