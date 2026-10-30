from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_name', 'status', 'created_at', 'total_display')
    list_filter = ('status',)
    inlines = [OrderItemInline]
    actions = ['faturar_pedidos']

    def total_display(self, obj):
        return f"R$ {obj.calculate_total()}"
    total_display.short_description = 'Total'

    # Ação customizada para testar o requisito RF-VND-003
    def faturar_pedidos(self, request, queryset):
        for order in queryset:
            if order.status != 'INVOICED':
                order.invoice_order()
        self.message_user(request, "Pedidos selecionados foram faturados com sucesso (Estoque baixado e Financeiro gerado).")
    faturar_pedidos.short_description = "Faturar Pedidos Selecionados"