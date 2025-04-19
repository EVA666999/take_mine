from django.contrib import messages
from django.shortcuts import redirect

def cannot_exchange_own_item(request, receiver_item):
    if receiver_item.user == request.user:
        messages.error(request, 'Нельзя предложить обмен на свой же товар!')
        return redirect('app:index')
    return None

def can_edit_item(request, item):
    if request.user != item.user:
        messages.error(request, 'У вас нет прав для редактирования этого объявления')
        return redirect('app:index')
    return None