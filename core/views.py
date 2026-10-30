from django.shortcuts import render, redirect
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from sales.models import Order
from inventory.models import Product
from finance.models import AccountReceivable, AccountPayable
from .forms import CompanyForm
from .forms import UserCreationForm, UserInviteForm, UserEditForm
from .models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import get_object_or_404

class InviteTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Cria um hash estável baseado apenas no ID e no estado ativo
        return str(user.pk) + str(user.is_active) + str(timestamp)

invite_token_generator = InviteTokenGenerator()

@login_required(login_url='/admin/login/')
def dashboard(request):
    # Se o usuário não tem empresa, não pode ver dados
    if not request.user.company:
        return render(request, 'core/no_company.html')  # Opcional: criar tela de aviso

    company = request.user.company

    # KPIs Rápidos
    total_vendas = Order.objects.filter(company=company, status='INVOICED').count()
    total_produtos = Product.objects.filter(company=company).count()

    # Contas Pendentes (Alertas)
    receber_pendente = AccountReceivable.objects.filter(company=company, status='PENDING').aggregate(Sum('amount'))['amount__sum'] or 0
    pagar_pendente = AccountPayable.objects.filter(company=company, status='PENDING').aggregate(Sum('amount'))['amount__sum'] or 0

    # Últimos pedidos para a tabela
    ultimos_pedidos = Order.objects.filter(company=company).order_by('-created_at')[:5]

    context = {
        'total_vendas': total_vendas,
        'total_produtos': total_produtos,
        'receber_pendente': receber_pendente,
        'pagar_pendente': pagar_pendente,
        'ultimos_pedidos': ultimos_pedidos,
    }
    return render(request, 'core/dashboard.html', context)

@login_required(login_url='/login/')
def user_list(request):
    # Apenas Admin pode ver lista de usuários (P-01) [cite: 48]
    if request.user.role != 'ADMIN':
        return redirect('dashboard')

    # Traz apenas usuários que pertencem à mesma empresa do administrador logado
    if request.user.company:
        users = User.objects.filter(company=request.user.company)
    else:
        users = User.objects.none()

    return render(request, 'core/user_list.html', {'users': users})


@login_required(login_url='/login/')
def user_create(request):
    # Apenas Admin pode criar usuários (P-01) [cite: 50]
    if request.user.role != 'ADMIN':
        return redirect('dashboard')

    if request.method == 'POST':

        form = UserInviteForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.company = request.user.company # Define a empresa do novo usuário igual à do admin que está criando
            user.set_unusable_password()  # O usuário não tem senha ainda
            user.save()

            # --- GERAÇÃO DO LINK MÁGICO ---
            token = invite_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(str(user.pk)))

            # Cria o link absoluto (ex: http://127.0.0.1:8000/reset/MQ/ad3-f9...)
            link = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )

            # --- ENVIO DO E-MAIL ---
            subject = f'Convite para acessar o Datalume OS - {request.user.company.nome_fantasia}'
            message = f"""
                        Olá, {user.first_name}!

                        Você foi convidado para acessar o sistema Datalume OS pela empresa {request.user.company.nome_fantasia}.

                        Para definir sua senha e acessar o sistema, clique no link abaixo:
                        {link}
                        """

            send_mail(subject, message, 'noreply@datalumeos.com.br', [user.email])
            messages.success(request, f"Convite enviado com sucesso para {user.email}!")

            return redirect('user_list')
    else:
        form = UserInviteForm()

    return render(request, 'core/user_form.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def company_settings(request):
    # Verifica se o usuário tem empresa vinculada
    if not request.user.company:
        messages.error(request, "Seu usuário não está vinculado a nenhuma empresa.")
        return redirect('dashboard')

    # Apenas ADMIN deve editar dados da empresa (Regra de negócio implícita)
    if request.user.role != 'ADMIN':
        messages.warning(request, "Apenas administradores podem alterar configurações da empresa.")
        return redirect('dashboard')

    company = request.user.company

    if request.method == 'POST':
        # request.FILES é necessário para upload de imagem (Logo)
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, "Dados da empresa atualizados com sucesso!")
            return redirect('company_settings')
    else:
        form = CompanyForm(instance=company)

    return render(request, 'core/company_settings.html', {'form': form})


# apps/core/views.py

def password_reset_confirm_custom(request, uidb64, token):
    # --- LIMPEZA BLINDADA ---
    # Remove espaços, quebras de linha (\n) e o sinal de igual (=) que vem de quebras de linha
    token = token.replace('=', '').replace('\n', '').replace('\r', '').strip()

    print(f"\n--- INICIANDO VALIDAÇÃO (LIMPO) PARA TOKEN: {token} ---")

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        print(f"DEBUG: Usuário encontrado: {user.username} (ID: {user.pk})")
    except Exception as e:
        user = None
        print(f"DEBUG ERRO: Falha ao decodificar usuário. Erro: {e}")

    # Validação
    valid = False
    if user is not None:
        valid = invite_token_generator.check_token(user, token)

    if valid:
        print("DEBUG SUCESSO: Token válido! Exibindo formulário.")
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Senha definida com sucesso!")
                return redirect('login')
        else:
            form = SetPasswordForm(user)

        return render(request, 'registration/password_reset_confirm.html', {
            'form': form,
            'validlink': True
        })
    else:
        print(f"DEBUG ERRO FINAL: Token inválido mesmo após limpeza.")
        return render(request, 'registration/password_reset_confirm.html', {
            'validlink': False
        })

@login_required(login_url='login')
def user_edit(request, pk):
    # Busca o usuário ou dá erro 404
    user_to_edit = get_object_or_404(User, pk=pk)

    # SEGURANÇA: Só Admin pode editar E só pode editar gente da PRÓPRIA empresa
    if request.user.role != 'ADMIN' or user_to_edit.company != request.user.company:
        messages.error(request, "Você não tem permissão para editar este usuário.")
        return redirect('user_list')

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, f"Dados de {user_to_edit.username} atualizados com sucesso!")
            return redirect('user_list')
    else:
        form = UserEditForm(instance=user_to_edit)

    return render(request, 'core/user_edit.html', {'form': form, 'user_to_edit': user_to_edit})


# --- REENVIAR E-MAIL DE SENHA ---
@login_required(login_url='login')
def user_resend_invite(request, pk):
    user_to_reset = get_object_or_404(User, pk=pk)

    # SEGURANÇA MESMA COISA
    if request.user.role != 'ADMIN' or user_to_reset.company != request.user.company:
        return redirect('dashboard')

    # Gera link usando nosso gerador blindado
    token = invite_token_generator.make_token(user_to_reset)
    uid = urlsafe_base64_encode(force_bytes(str(user_to_reset.pk)))

    link = request.build_absolute_uri(
        reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
    )

    # IMPRIME NO CONSOLE
    print("\n" + "=" * 50)
    print(f"REENVIO DE SENHA PARA {user_to_reset.email}:")
    print(link)
    print("=" * 50 + "\n")

    # Envia e-mail
    subject = f'Redefinição de Senha - {request.user.company.nome_fantasia}'
    message = f"O administrador solicitou a redefinição da sua senha. Clique aqui: {link}"
    send_mail(subject, message, 'noreply@datalumeos.com.br', [user_to_reset.email])

    messages.success(request, f"E-mail de redefinição enviado para {user_to_reset.email}.")
    return redirect('user_list')