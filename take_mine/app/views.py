from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect

from .permissions import cannot_exchange_own_item, can_edit_item
from .utils import get_page_context
from django.db.models import Q

from .models import Item, Category, User, ExchangeProposal
from django.contrib.auth.decorators import login_required
from .forms import CategoryForm, ItemForm, ExchangeProposalForm
from django.contrib import messages

def index(request):
    query = request.GET.get("q")
    category_id = request.GET.get("category")
    condition = request.GET.get("condition")

    # Получаем ID предметов, участвующих в принятых обменах
    exchanged_items = ExchangeProposal.objects.filter(
        status='принята'
    ).values_list('ad_sender', 'ad_receiver')
    
    # Преобразуем список кортежей в плоский список ID
    exchanged_items_ids = []
    for sender_id, receiver_id in exchanged_items:
        exchanged_items_ids.extend([sender_id, receiver_id])
    
    # Получаем все предметы, исключая те, которые участвовали в успешном обмене
    items = Item.objects.exclude(id__in=exchanged_items_ids).order_by("-created_at")

    if query:
        items = items.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if category_id:
        items = items.filter(category_id=category_id)

    if condition:
        items = items.filter(condition=condition)

    context = get_page_context(items, request)
    context.update({
        "categories": Category.objects.all(),
        "conditions": Item.CONDITION_CHOICES,
    })
    return render(request, "index.html", context)



@login_required
def item_create(request):
    if request.method == "POST":
        form = ItemForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.save()
            messages.success(request, 'Объявление успешно создано!')
            return redirect("app:index")
    else:
        form = ItemForm()
    return render(request, "app/create_item.html", {"form": form})

def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Категория "{category.name}" успешно создана!')
            return redirect('app:index')
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'title': 'Создание новой категории'
    }
    return render(request, 'app/create_category.html', context)


@login_required
def item_edit(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    
    permission_check = can_edit_item(request, item)
    if permission_check:
        return permission_check
    
    if request.method == "POST":
        form = ItemForm(request.POST, files=request.FILES or None, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, 'Объявление успешно обновлено')
            return redirect('users:profile', username=request.user.username)
    else:
        form = ItemForm(instance=item)
    
    context = {"form": form, "item": item}
    return render(request, "app/item_edit.html", context)


@login_required
def item_delete(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    
    if request.user != item.user:
        messages.error(request, 'У вас нет прав для удаления этого объявления')
        return redirect('app:index')
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Объявление успешно удалено')
        return redirect('users:profile', username=request.user.username)
    
    return render(request, 'app/item_delete.html', {'item': item})

@login_required
def create_exchange_proposal(request, item_id):
    receiver_item = get_object_or_404(Item, id=item_id)
    
    permission_check = cannot_exchange_own_item(request, receiver_item)
    if permission_check:
        return permission_check
    
    if request.method == 'POST':
        sender_item_id = request.POST.get('sender_item_id')
        sender_item = get_object_or_404(Item, id=sender_item_id, user=request.user)
        
        ExchangeProposal.objects.create(
            ad_sender=sender_item,
            ad_receiver=receiver_item,
            comment=request.POST.get('comment', '')
        )
        
        messages.success(request, 'Предложение обмена отправлено!')
        return redirect('app:exchanges')
        
    items = Item.objects.filter(user=request.user)
    return render(request, 'app/exchange_proposal.html', {
        'receiver_item': receiver_item, 
        'items': items
    })



@login_required
def exchanges_list(request):
    view = request.GET.get('view', 'all')
    status = request.GET.get('status', 'all')
    
    sent_proposals = ExchangeProposal.objects.filter(
        ad_sender__user=request.user
    ).select_related('ad_sender', 'ad_receiver', 'ad_sender__user', 'ad_receiver__user')
    
    received_proposals = ExchangeProposal.objects.filter(
        ad_receiver__user=request.user
    ).select_related('ad_sender', 'ad_receiver', 'ad_sender__user', 'ad_receiver__user')
    
    if status != 'all':
        sent_proposals = sent_proposals.filter(status=status)
        received_proposals = received_proposals.filter(status=status)
    
    context = {
        'sent_proposals': sent_proposals,
        'received_proposals': received_proposals,
        'view': view,
        'status': status if status else 'all',
    }
    
    return render(request, 'app/exchanges_list.html', context)

@login_required
def accept_proposal(request, proposal_id):
    """
    Принятие предложения обмена.
    Логика: вещь доступна для обмена сколько угодно раз. 
    Как только предложение принято - обе вещи помечаются статусом 'принято', 
    остальные предложения по этим вещам становятся 'забрали'.
    """
    proposal = get_object_or_404(ExchangeProposal, id=proposal_id)
    
    if proposal.status != 'ожидает':
        messages.error(request, 'Предложение уже обработано')
        return redirect('app:exchanges')
    
    if proposal.ad_receiver.user != request.user:
        return HttpResponseForbidden("Вы не можете принять это предложение")
    
    if request.method == 'POST':
        sender_item = proposal.ad_sender
        receiver_item = proposal.ad_receiver
        
        sender_user = sender_item.user
        receiver_user = receiver_item.user
        
        sender_item.user = receiver_user
        receiver_item.user = sender_user
        
        sender_item.save()
        receiver_item.save()
        
        ExchangeProposal.objects.filter(
            Q(ad_sender=sender_item) | Q(ad_receiver=sender_item) |
            Q(ad_sender=receiver_item) | Q(ad_receiver=receiver_item),
            status='ожидает'
        ).update(status='забрали')
        
        proposal.status = 'принята'
        proposal.save()
        
        messages.success(request, 'Обмен успешно завершен!')
        return redirect('app:exchanges')
    
    return render(request, 'app/accept_proposal.html', {'proposal': proposal})

@login_required
def reject_proposal(request, proposal_id):
    """Отклонение предложения обмена"""
    proposal = get_object_or_404(ExchangeProposal, id=proposal_id)
    
    # Проверка статуса предложения
    if proposal.status != 'ожидает':
        messages.error(request, 'Предложение уже обработано')
        return redirect('app:exchanges')
    
    # Проверка прав пользователя
    if proposal.ad_receiver.user != request.user:
        return HttpResponseForbidden("Вы не можете отклонить это предложение")
    
    if request.method == 'POST':
        proposal.status = 'отклонена'
        proposal.save()
        
        messages.success(request, 'Предложение отклонено')
        return redirect('app:exchanges')
    
    return render(request, 'app/reject_proposal.html', {'proposal': proposal})