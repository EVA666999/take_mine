from django.forms import ModelForm
from django import forms
from .models import Item, Category

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