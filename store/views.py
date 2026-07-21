from django.shortcuts import render


def product_list(request, slug=None):
    return render(request, 'store/product_list.html')


def product_detail(request, id, slug):
    return render(request, 'store/product_detail.html')
