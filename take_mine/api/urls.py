from django.urls import include, path
from rest_framework import routers

from .views import (
    AcceptProposalView,
    CategoryViewSet,
    ExchangeProposalViewSet,
    ItemViewSet,
    MyItemsViewSet,
    MyProposalsViewSet,
    RejectProposalView,
)

router = routers.DefaultRouter()
router.register(r"categories", CategoryViewSet)
router.register(r"items", ItemViewSet)
router.register(r"exchange-proposals", ExchangeProposalViewSet)
router.register(r"my-proposals", MyProposalsViewSet, basename="my-proposals")
router.register(r"my-items", MyItemsViewSet, basename="my-items")


urlpatterns = [
    path(
        "my-proposals/<int:pk>/accept/",
        AcceptProposalView.as_view(),
        name="accept_proposal",
    ),
    path(
        "my-proposals/<int:pk>/reject/",
        RejectProposalView.as_view(),
        name="reject_proposal",
    ),
    path("", include(router.urls)),
]
