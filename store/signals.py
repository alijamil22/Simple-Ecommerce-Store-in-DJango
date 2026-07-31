from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Order


@receiver(post_save, sender=Order)
def send_order_confirmation(sender, instance, created, **kwargs):
    if created and instance.user.email:
        subject = f'Order #{instance.id} confirmed - Simple E-Commerce Store'
        body = render_to_string('store/order/order_email.txt', {'order': instance})
        send_mail(subject, body, None, [instance.user.email])
