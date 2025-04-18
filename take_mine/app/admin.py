from django.contrib import admin
from .models import Category, Item, ExchangeProposal

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'condition', 'created_at')
    list_filter = ('category', 'condition', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'

class ExchangeProposalAdmin(admin.ModelAdmin):
    list_display = ('ad_sender', 'ad_receiver', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('comment',)
    date_hierarchy = 'created_at'
    raw_id_fields = ('ad_sender', 'ad_receiver')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(ExchangeProposal, ExchangeProposalAdmin)