from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth import login, logout
from .models import Category, Product
from .cart import Cart
from .forms import RegistrationForm


def product_list(request, slug=None):
    category = None
    products = Product.objects.filter(available=True)

    if slug:
        category = get_object_or_404(Category, slug=slug)
        products = products.filter(category=category)

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
    return redirect('store:product_list')
