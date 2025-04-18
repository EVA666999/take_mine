from .models import ExchangeProposal

def exchange_proposals_count(request):
    """
    Добавляет счетчик непрочитанных предложений обмена в контекст всех шаблонов
    """
    if request.user.is_authenticated:
        count = ExchangeProposal.objects.filter(
            ad_receiver__user=request.user,
            status='ожидает'
        ).count()
        return {'pending_exchanges_count': count}
    return {'pending_exchanges_count': 0}