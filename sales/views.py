from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Order, OrderItem
from inventory.models import Product


@login_required(login_url='login')
def order_create(request):
    company = request.user.company
    if not company:
        return redirect('dashboard')

    if request.method == 'POST':
        client_name = request.POST.get('client_name')

        # Pega as listas de dados enviadas pelo formulário
        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')

        # Usa transação atômica: ou salva tudo (pedido + itens) ou não salva nada (segurança de dados)
        with transaction.atomic():
            order = Order.objects.create(company=company, client_name=client_name, status='BUDGET')

            for p_id, qty in zip(product_ids, quantities):
                if int(qty) > 0:
                    product = Product.objects.get(id=p_id, company=company)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=int(qty),
                        unit_price=product.sale_price  # Trava o preço no momento da venda
                    )

            return redirect('dashboard')

    # GET: Mostra a tela
    products = Product.objects.filter(company=company)
    return render(request, 'sales/order_create.html', {'products': products})