from django.contrib import admin
from .models import Order, OrderItem, PaymentMethod

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'total_amount', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email']
    inlines = [OrderItemInline]

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['user', 'card_type', 'last_four', 'is_default']
    list_filter = ['card_type', 'is_default']