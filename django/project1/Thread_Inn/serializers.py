from rest_framework import serializers
from .models import Product, Cart

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image', 'category', 'created_at', 'updated_at']

class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'quantity', 'added_at'] 