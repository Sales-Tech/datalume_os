# apps/finance/models.py
from django.db import models
from core.models import Company

class FinancialCategory(models.Model):
    """
    RF-FIN-004: Categorias Financeiras 
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    TYPE_CHOICES = (
        ('INCOME', 'Receita'),
        ('EXPENSE', 'Despesa'),
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    def __str__(self):
        return f"{self.get_type_display()} - {self.name}"

class AccountPayable(models.Model):
    """
    RF-FIN-001: Cadastro de Contas a Pagar [cite: 73]
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    STATUS_CHOICES = (
        ('PENDING', 'Pendente'),
        ('PAID', 'Paga'),
        ('OVERDUE', 'Atrasada'),
    )
    supplier = models.CharField(max_length=255) # [cite: 75]
    description = models.CharField(max_length=255)
    category = models.ForeignKey(FinancialCategory, on_delete=models.PROTECT, limit_choices_to={'type': 'EXPENSE'})
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_date = models.DateField(null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

class AccountReceivable(models.Model):
    """
    RF-FIN-002: Cadastro de Contas a Receber [cite: 80]
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    STATUS_CHOICES = (
        ('PENDING', 'Pendente'),
        ('RECEIVED', 'Recebida'),
        ('OVERDUE', 'Atrasada'),
    )
    client = models.CharField(max_length=255) # [cite: 82]
    description = models.CharField(max_length=255)
    category = models.ForeignKey(FinancialCategory, on_delete=models.PROTECT, limit_choices_to={'type': 'INCOME'})
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    receipt_date = models.DateField(null=True, blank=True)
    amount_received = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)