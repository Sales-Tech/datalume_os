from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Company

# Personaliza o UserAdmin padrão para mostrar o campo 'role'
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'company', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Perfil e Empresa', {'fields': ('role', 'company')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Company)