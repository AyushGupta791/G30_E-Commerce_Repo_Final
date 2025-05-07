from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('confirmation/', views.order_confirmation, name='order_confirmation'),
]