from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'shipping_name', 'shipping_address', 'shipping_city',
            'shipping_postal_code', 'shipping_phone'
        ]
        widgets = {
            'shipping_name': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'shipping_city': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'shipping_name': 'Nome completo',
            'shipping_address': 'Indirizzo',
            'shipping_city': 'Città',
            'shipping_postal_code': 'CAP',
            'shipping_phone': 'Telefono',
        }