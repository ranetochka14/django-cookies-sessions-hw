from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

PRODUCTS = {
    1: {'name': 'Ноутбук', 'price': 500000},
    2: {'name': 'Смартфон', 'price': 300000},
    3: {'name': 'Беспроводные наушники', 'price': 45000},
    4: {'name': 'Механическая клавиатура', 'price': 35000},
    5: {'name': 'Игровая мышь', 'price': 25000},
}

def visits_view(request):
    visits = int(request.COOKIES.get('visits', 0)) + 1
    response = render(request, 'practice/visits.html', {'visits': visits})
    response.set_cookie('visits', str(visits), max_age=604800)
    return response

def visits_reset(request):
    response = redirect('visits')
    response.delete_cookie('visits')
    return response

# Задания 2 и 3: Sessions + Messages
def products_view(request):
    return render(request, 'practice/products.html', {'products': PRODUCTS})

def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_cost = 0

    for str_id, qty in cart.items():
        prod_id = int(str_id)
        if prod_id in PRODUCTS:
            product = PRODUCTS[prod_id]
            cost = product['price'] * qty
            total_cost += cost
            cart_items.append({
                'id': prod_id,
                'name': product['name'],
                'price': product['price'],
                'quantity': qty,
                'total': cost
            })

    return render(request, 'practice/cart.html', {'cart_items': cart_items, 'total_cost': total_cost})

def cart_add(request, product_id):
    product = PRODUCTS.get(product_id)
    if not product:
        messages.error(request, 'Товар не найден.')
        return redirect('products')

    cart = request.session.get('cart', {})
    str_id = str(product_id)
    cart[str_id] = cart.get(str_id, 0) + 1
    request.session['cart'] = cart

    messages.success(request, f'Товар «{product["name"]}» успешно добавлен в корзину.')
    return redirect('products')

def cart_remove(request, product_id):
    cart = request.session.get('cart', {})
    str_id = str(product_id)

    if str_id in cart:
        product_name = PRODUCTS.get(product_id, {}).get('name', 'Товар')
        del cart[str_id]
        request.session['cart'] = cart
        messages.warning(request, f'Товар «{product_name}» удалён из корзины.')
    else:
        messages.error(request, 'Попытка удалить отсутствующий товар из корзины.')

    return redirect('cart')

def cart_clear(request):
    if 'cart' in request.session:
        del request.session['cart']
    messages.info(request, 'Корзина очищена.')
    return redirect('cart')

PROMO_SALT = 'promo-discount-salt'

def promo_generate(request):
    signer = TimestampSigner(salt=PROMO_SALT)
    promo_token = signer.sign('DISCOUNT_20')
    return render(request, 'practice/promo.html', {'promo_token': promo_token})

def promo_check(request):
    token = request.GET.get('code', '').strip()
    status = None
    promo_value = None

    if token:
        signer = TimestampSigner(salt=PROMO_SALT)
        try:
            promo_value = signer.unsign(token, max_age=60)
            status = 'valid'
        except SignatureExpired:
            status = 'expired'
        except BadSignature:
            status = 'invalid'

    return render(request, 'practice/promo_check.html', {
        'status': status,
        'promo_value': promo_value,
        'checked_code': token
    })