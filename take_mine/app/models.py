from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.contrib.auth import get_user_model

User = get_user_model()
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100, default=slugify('category'))
    
    def __str__(self):
        
        return self.name
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']


class Item(models.Model):
    CONDITION_CHOICES = [
        ('new', 'Новый'),
        ('used', 'Б/у'),
        ('for_parts', 'На запчасти')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=200)
    description = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='used')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Вещь"
        verbose_name_plural = "Вещи"  
    
class ExchangeProposal(models.Model):
    STATUS_CHOICES = [
        ('ожидает', 'Ожидает'),
        ('принята', 'Принята'),
        ('отклонена', 'Отклонена'),
    ]
    
    ad_sender = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='sent_proposals') # отправитель
    ad_receiver = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='received_proposals') # получатель
    comment = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ожидает')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Обмен: {self.ad_sender} → {self.ad_receiver} ({self.status})"
    
    class Meta:
        verbose_name = "Предложение обмена"
        verbose_name_plural = "Предложения обмена"
        ordering = ['-created_at']