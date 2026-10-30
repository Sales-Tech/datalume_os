from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import views  # Importe a view que criamos
from django.conf import settings
from django.conf.urls.static import static
from core.forms import UserLoginForm

# ... urlpatterns existentes ...


urlpatterns = [
    path('admin/', admin.site.urls),
    # Rotas de Autenticação
    path('login/', auth_views.LoginView.as_view(authentication_form=UserLoginForm), name='login'),
    path('logout/', views.logout_view, name='logout'),


    # Rota que o usuário acessa ao clicar no e-mail
    path('reset/<uidb64>/<token>/', views.password_reset_confirm_custom, name='password_reset_confirm'),

    # Rota de sucesso após definir a senha
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),

    # Rotas do Sistema
    path('', views.dashboard, name='dashboard'),
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_create, name='user_create'),
    path('users/edit/<int:pk>/', views.user_edit, name='user_edit'),
    path('users/resend/<int:pk>/', views.user_resend_invite, name='user_resend_invite'),

    # Empresa
    path('settings/company/', views.company_settings, name='company_settings'),

    # Sales
    path('sales/', include('sales.urls')),
]

# Configuração para servir imagens (Logo da empresa) em modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)