# apps/core/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from .models import User
from .models import Company
from .validators import validate_cnpj

class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Senha")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Criptografa a senha
        if commit:
            user.save()
        return user

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'nome_fantasia', 'razao_social', 'cnpj', 'inscricao_estadual',
            'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado',
            'logo'
        ]
        widgets = {
            'estado': forms.TextInput(attrs={'placeholder': 'UF', 'maxlength': '2'}),
            'cnpj': forms.TextInput(attrs={'placeholder': '00.000.000/0000-00'}),
        }

    # Método Clean específico para o campo CNPJ
    def clean_cnpj(self):
        cnpj_raw = self.cleaned_data.get('cnpj')

        # 1. Chama nosso validador matemático
        # Se falhar, ele lança o erro automaticamente e o Django mostra no HTML
        validate_cnpj(cnpj_raw)

        # 2. Se passou, vamos retornar apenas os números para salvar limpo no banco
        import re
        return re.sub(r'[^0-9]', '', cnpj_raw)

class UserInviteForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'role']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'role', 'is_active']
        labels = {
            'is_active': 'Usuário Ativo (Acesso Permitido)'
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Verifica se o email já existe em OUTRO usuário (excluindo o atual)
        if self.instance.pk and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este e-mail já está em uso por outra pessoa.")
        return email


class UserLoginForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # 1. Tenta autenticar normalmente
            self.user_cache = authenticate(self.request, username=username, password=password)

            # 2. Se falhou (None), vamos investigar o motivo
            if self.user_cache is None:
                try:
                    # Busca o usuário no banco (sem logar) para investigar
                    user_temp = User.objects.get(username=username)

                    # Se a senha estiver correta...
                    if user_temp.check_password(password):
                        # ...mas o usuário estiver INATIVO
                        if not user_temp.is_active:
                            raise forms.ValidationError(
                                "Esta conta foi desativada pelo administrador. Entre em contato com o suporte.",
                                code='inactive',
                            )
                except User.DoesNotExist:
                    # Se o usuário não existe, não fazemos nada (cairá no erro genérico abaixo)
                    pass

                # Se chegou aqui, é senha errada ou usuário inexistente (Erro Padrão)
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                # Se autenticou com sucesso, confirma o login
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data