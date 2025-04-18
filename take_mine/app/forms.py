from django.forms import ModelForm
from django import forms
from .models import Item, Category, ExchangeProposal

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'slug')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Введите название категории'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Введите slug (необязательно)'
            })
        }

class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ("title", "description", "image_url", "category", "condition")
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Введите название вещи'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Введите описание (необязательно)',
                'rows': 3
            }),
            'image_url': forms.URLInput(attrs={ 
                'class': 'form-control', 
                'placeholder': 'Вставьте ссылку на изображение (необязательно)'
            }),
            'category': forms.Select(attrs={ 
                'class': 'form-control', 
            }),
            'condition': forms.Select(attrs={
                'class': 'form-control', 
            }),
        }

class ExchangeProposalForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = ['ad_receiver', 'comment']
        widgets = {
            'ad_receiver': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Выберите товар для обмена'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Оставьте комментарий (необязательно)',
                'rows': 3
            }),
        }