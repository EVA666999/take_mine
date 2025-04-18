from django.shortcuts import get_object_or_404, render
from .utils import get_page_context
from .models import Item, Category

def index(request):
    items = Item.objects.all()
    context = get_page_context(items, request)
    return render(request, "index.html", context)

def create_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    items = Category.objects.select_related("category")[:10]
    context = {
        "category": category,
        "items": items,
    }
    context.update(get_page_context(category.items.all(), request))
    return render(request, "category/group_list.html", context)