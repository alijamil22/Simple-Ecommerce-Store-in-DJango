from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Category, Product, Order, OrderItem
from .cart import Cart
from .forms import RegistrationForm, CheckoutForm


def product_list(request, slug=None):
    category = None
    products = Product.objects.filter(available=True)

    if slug:
        category = get_object_or_404(Category, slug=slug)
        products = products.filter(category=category)

    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    return render(request, 'store/product_list.html', {
        'category': category,
        'products': products,
    })


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    return render(request, 'store/product_detail.html', {'product': product})


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'store/cart/detail.html', {'cart': cart})


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1
    if cart.add(product, quantity):
        messages.success(request, f'{product.name} added to cart.')
    else:
        messages.error(request, f'Cannot add {product.name}. Only {product.stock} in stock.')
    return redirect('store:product_detail', id=product.id, slug=product.slug)


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, f'{product.name} removed from cart.')
    return redirect('store:cart_detail')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully.')
            return redirect('store:product_list')
    else:
        form = RegistrationForm()
    return render(request, 'store/auth/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('store:product_list')


@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/auth/profile.html', {'orders': orders})


@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, 'Your cart is empty.')
        return redirect('store:cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            if order.payment_method == 'card':
                order.paid = True
            order.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                )
                product = item['product']
                product.stock -= item['quantity']
                product.save()

            cart.clear()

            if order.payment_method == 'card':
                messages.success(request, 'Payment successful. Order confirmed.')
            else:
                messages.success(request, 'Order placed. Pay on delivery.')

            return redirect('store:order_confirmation', order_id=order.id)
    else:
        form = CheckoutForm()

    return render(request, 'store/order/checkout.html', {
        'form': form,
        'cart': cart,
    })


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order/confirmation.html', {'order': order})
