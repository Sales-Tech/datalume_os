# apps/inventory/models.py
from django.db import models
from core.models import Company

class Product(models.Model):
    """
    RF-VND-001: Gestão de Produtos e Serviços [cite: 99]
    RF-EST-001: Controle de Estoque [cite: 120]
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='products')

    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=50) # [cite: 101]
    description = models.TextField(blank=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=10, default='UN')
    current_stock = models.IntegerField(default=0) # Quantidade atual [cite: 123]

    class Meta:
        # O SKU deve ser único APENAS dentro da mesma empresa
        unique_together = ('company', 'sku')

    def __str__(self):
        return f"{self.sku} - {self.name}"

class StockEntry(models.Model):
    """
    RF-EST-002: Registro de Compras [cite: 126]
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    supplier = models.CharField(max_length=255) # Simplificado para MVP
    date = models.DateField(auto_now_add=True)
    note = models.TextField(blank=True)

class StockEntryItem(models.Model):
    entry = models.ForeignKey(StockEntry, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Atualiza o estoque ao salvar uma entrada [cite: 131]
        super().save(*args, **kwargs)
        self.product.current_stock += self.quantity
        self.product.save()