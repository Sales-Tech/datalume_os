from django.contrib import admin
from .models import FinancialCategory, AccountPayable, AccountReceivable

@admin.register(AccountPayable)
class AccountPayableAdmin(admin.ModelAdmin):
    list_display = ('description', 'supplier', 'amount', 'due_date', 'status')
    list_filter = ('status', 'due_date')
    search_fields = ('description', 'supplier')

@admin.register(AccountReceivable)
class AccountReceivableAdmin(admin.ModelAdmin):
    list_display = ('description', 'client', 'amount', 'due_date', 'status')
    list_filter = ('status', 'due_date')

admin.site.register(FinancialCategory)