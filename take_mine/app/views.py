from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

from take_mine.app.models import Item

def home(request):
    return render(request, 'app/home.html', {'items': Item.objects.all()})