from django import template
from store.cart import Cart

register = template.Library()


@register.filter
def cart_count(session):
    cart = Cart(session)
    return len(cart)
