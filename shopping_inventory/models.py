from django.db import models

class Customer(models.Model):
    cust_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=12)

class Product(models.Model):
    prod_id = models.AutoField(primary_key=True)
    prod_name = models.CharField(max_length=50)
    price = models.FloatField()
    prod_weight = models.FloatField() #Has to assume the user entered in kg
    in_stock = models.IntegerField()


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    cust_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    po_number = models.CharField(max_length=50)
    order_date = models.CharField(max_length=50)

class Cart(models.Model):
    cust_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    prod_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

