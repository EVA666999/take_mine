from rest_framework import serializers
from app.models import Category, Item, ExchangeProposal


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id', 'slug']


class ItemSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field="name"
    )
    class Meta:
        model = Item
        fields = ['id', 'title', 'description', 'image_url', 'category', 'condition']
        read_only_fields = ['id', 'user', 'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = str(instance.user)
        return representation

    
    
class ExchangeProposalSerializer(serializers.ModelSerializer):
    ad_sender = serializers.SlugRelatedField(
        queryset=Item.objects.all(), 
        slug_field='title',
        write_only=True
    )
    ad_receiver = serializers.SlugRelatedField(
        queryset=Item.objects.all(), 
        slug_field='title',
        write_only=True
    )
    
    def validate(self, data):
        """
        Проверка прав пользователя
        """
        ad_sender = data.get('ad_sender')
        ad_receiver = data.get('ad_receiver')
        
        if ad_sender.user != self.context['request'].user:
            raise serializers.ValidationError(
                "Вы можете предлагать обмен только своих предметов"
            )
        
        if ad_receiver.user == self.context['request'].user:
            raise serializers.ValidationError(
                "Нельзя предлагать обмен на свой собственный товар"
            )
            
        return data
    
    class Meta:
        model = ExchangeProposal
        fields = [
            'id', 'ad_sender', 'ad_receiver', 
            'comment', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'status']


class MyProposalsSerializer(serializers.ModelSerializer):
    ad_sender_title = serializers.CharField(source='ad_sender.title', read_only=True)
    ad_receiver_title = serializers.CharField(source='ad_receiver.title', read_only=True)
    ad_sender_user = serializers.CharField(source='ad_sender.user.username', read_only=True)
    ad_receiver_user = serializers.CharField(source='ad_receiver.user.username', read_only=True)

    class Meta:
        model = ExchangeProposal
        fields = [
            'id', 
            'ad_sender', 
            'ad_receiver', 
            'ad_sender_title', 
            'ad_receiver_title',
            'ad_sender_user',
            'ad_receiver_user',
            'status', 
            'created_at', 
            'comment'
        ]
        read_only_fields = ['status']