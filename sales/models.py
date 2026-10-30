# apps/sales/models.py
from django.db import models
from django.utils import timezone
from inventory.models import Product
from finance.models import AccountReceivable, FinancialCategory
from core.models import Company


class Order(models.Model):
    """
    RF-VND-002: Pedidos de Venda e Orçamentos [cite: 104]
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    STATUS_CHOICES = (
        ('BUDGET', 'Orçamento'),
        ('CONFIRMED', 'Pedido Confirmado'),
        ('INVOICED', 'Faturado'),  # [cite: 114]
        ('CANCELLED', 'Cancelado'),
    )
    client_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='BUDGET')

    def calculate_total(self):
        return sum(item.total_price() for item in self.items.all())  # [cite: 108]

    def invoice_order(self):
        """
        RF-VND-003: Lógica de Faturamento [cite: 112]
        """
        if self.status == 'INVOICED':
            return  # Já faturado

        # 1. Atualizar Status
        self.status = 'INVOICED'
        self.save()

        # 2. Baixa no Estoque 
        for item in self.items.all():
            product = item.product
            product.current_stock -= item.quantity
            product.save()

        # 3. Gerar Conta a Receber 
        # Assume-se que existe uma categoria padrão de Vendas, senão cria uma genérica
        category, _ = FinancialCategory.objects.get_or_create(
            name='Vendas de Produtos',
            company=self.company,
            defaults={'type': 'INCOME'}
        )

        AccountReceivable.objects.create(
            company=self.company,
            client=self.client_name,
            description=f"Pedido #{self.id}",
            category=category,
            amount=self.calculate_total(),
            due_date=timezone.now().date()  # Simplificado para hoje
        )


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def total_price(self):
        return self.quantity * self.unit_price