from rest_framework import routers

from .views import CategoryViewSet, ItemViewSet, ExchangeProposalViewSet, MyProposalsViewSet

router = routers.DefaultRouter()

router.register(r'categories', CategoryViewSet)
router.register(r'items', ItemViewSet)
router.register(r'exchange-proposals', ExchangeProposalViewSet)
router.register(r'my-proposals', MyProposalsViewSet, basename='my-proposals')