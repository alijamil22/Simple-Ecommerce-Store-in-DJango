from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Category, Product
from .cart import Cart


def product_list(request, slug=None):
    categories = Category.objects.all()
    category = None
    products = Product.objects.filter(available=True)

    if slug:
        category = get_object_or_404(Category, slug=slug)
        products = products.filter(category=category)

    return render(request, 'store/product_list.html', {
        'category': category,
        'categories': categories,
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
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product, quantity)
    return redirect('store:cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('store:cart_detail')
