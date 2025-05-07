from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'email@example.com'}))
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Full Name'}))
    street_address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '123 Main St'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'New York'}))
    state = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'NY'}))
    zip_code = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '10001'}))
    country = forms.ChoiceField(choices=[
        ('', 'Select country'),
        ('IN', 'India'),
        ('US', 'United States'),
        ('CA', 'Canada'),
        ('UK', 'United Kingdom'),
        ('AU', 'Australia'),
        ('DE', 'Germany'),
        ('FR', 'France'),
        ('JP', 'Japan'),
    ])
    
    class Meta:
        model = Order
        fields = ['email', 'name', 'street_address', 'city', 'state', 'zip_code', 'country']

class PaymentForm(forms.Form):
    card_number = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '1234 5678 9012 3456', 'maxlength': '19'}),
        required=True
    )
    expiry = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'MM/YY', 'maxlength': '5'}),
        required=True
    )
    cvv = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '123', 'maxlength': '4'}),
        required=True
    )