from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['address', 'city', 'postal_code', 'phone', 'payment_method']
        widgets = {
            'payment_method': forms.RadioSelect,
        }
