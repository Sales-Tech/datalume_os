# apps/core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser


class Company(models.Model):
    """
    RF-CFG-001: Configuração da Empresa
    Agora transformada em entidade 'Company' para suportar Multi-tenancy.
    """
    razao_social = models.CharField(max_length=255, verbose_name="Razão Social")
    nome_fantasia = models.CharField(max_length=255, verbose_name="Nome Fantasia")
    cnpj = models.CharField(max_length=18, unique=True, verbose_name="CNPJ")

    # Endereço e Contato
    inscricao_estadual = models.CharField(max_length=50, blank=True)
    inscricao_municipal = models.CharField(max_length=50, blank=True)
    logradouro = models.CharField(max_length=255)
    numero = models.CharField(max_length=20, verbose_name="Número")
    complemento = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)

    # Branding
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome_fantasia


class User(AbstractUser):
    """
    RF-CFG-002: Gestão de Usuários
    Agora vinculado a uma empresa específica.
    """
    ROLE_CHOICES = (
        ('ADMIN', 'Administrador (P-01)'),
        ('MANAGER', 'Gestor (P-02)'),
        ('OPERATOR', 'Operador (P-03)'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='OPERATOR')

    # Link com a Empresa (Essencial para SaaS)
    # null=True permite que superusuários do sistema (nós) existam sem empresa
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name='users')