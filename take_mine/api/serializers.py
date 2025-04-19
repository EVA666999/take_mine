from rest_framework import serializers
from app.models import Category, Item, ExchangeProposal


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ItemSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field="name"
    )
    class Meta:
        model = Item
        fields = ['id', 'title', 'description', 'image_url', 'category', 'condition']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = str(instance.user)
        return representation

    


class ExchangeProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeProposal
        fields = ['id', 'ad_sender', 'ad_receiver', 'comment']
