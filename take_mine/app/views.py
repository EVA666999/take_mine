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

    items = Item.objects.all().order_by("-created_at")

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
def accept_exchange(request, proposal_id):
    proposal = get_object_or_404(ExchangeProposal, id=proposal_id)
    
    if proposal.status != 'ожидает':
        messages.error(request, 'Это предложение уже обработано')
        return redirect('app:exchanges')
    
    proposal.status = 'принята'
    proposal.save()
    
    messages.success(request, f'Вы приняли предложение обмена от {proposal.ad_sender.user.username}')
    return redirect('app:exchanges')

@login_required
def reject_exchange(request, proposal_id):
    proposal = get_object_or_404(ExchangeProposal, id=proposal_id)
    
    if proposal.status != 'ожидает':
        messages.error(request, 'Это предложение уже обработано')
        return redirect('app:exchanges')
    
    proposal.status = 'отклонена'
    proposal.save()
    
    messages.success(request, f'Вы отклонили предложение обмена от {proposal.ad_sender.user.username}')
    return redirect('app:exchanges')