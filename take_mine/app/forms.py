from django.forms import ModelForm
from django import forms
from .models import Item, Category
from .models import Profile


class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ("title", "description", "image_url", "category", "condition")
