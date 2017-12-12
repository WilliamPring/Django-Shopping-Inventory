# Assignment:   SOA #4
# Date:         2017-12-11
# Name:         Denys Politiuk, William Pring, Naween Mehanmal
# Filename:     admin.py
# Description:  File that imports models to the admin change to allow editing database in the admin page

from django.contrib import admin
from .models import Customer, Product, Order, Cart

# Register your models here.
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Cart)
