from rest_framework import routers

from .views import CategoryViewSet, ItemViewSet, ExchangeProposalViewSet

router = routers.DefaultRouter()

router.register(r'categories', CategoryViewSet)
router.register(r'items', ItemViewSet)
router.register(r'exchange-proposals', ExchangeProposalViewSet)