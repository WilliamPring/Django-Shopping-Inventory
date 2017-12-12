# Assignment:   SOA #4
# Date:         2017-12-11
# Name:         Denys Politiuk, William Pring, Naween Mehanmal
# Filename:     serializers.py
# Description:  File with serializers for database models

from rest_framework import serializers
from .models import Customer, Product, Order, Cart

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        #fields = ('order_id',)
        fields = '__all__'