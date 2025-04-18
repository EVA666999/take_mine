from django.shortcuts import render, redirect
from .utils import get_page_context
from .models import Item, Category
from .forms import CategoryForm
from django.contrib import messages

def index(request):
    items = Item.objects.all()
    context = get_page_context(items, request)
    return render(request, "index.html", context)

def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Категория "{category.name}" успешно создана!')
            return redirect('home')  # или на страницу списка категорий
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'title': 'Создание новой категории'
    }
    return render(request, 'category/create_category.html', context)