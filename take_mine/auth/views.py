from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from api.serializers import ItemSerializer
from app.models import Item

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]  # Только для аутентифицированных

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)