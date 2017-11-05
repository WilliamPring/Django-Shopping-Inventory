from django.db import models

class Customer(models.Model):
    cust_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=12)
    
    def __str__(self):
        
        return self.first_name + " " + self.last_name

class Product(models.Model):
    prod_id = models.AutoField(primary_key=True)
    prod_name = models.CharField(max_length=50)
    price = models.FloatField()
    prod_weight = models.FloatField() #Has to assume the user entered in kg
    in_stock = models.IntegerField()


    def __str__(self):
        return self.prod_name


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    cust_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    po_number = models.CharField(max_length=50, blank=True)
    order_date = models.DateField()
    def __str__(self):
        return str(self.order_id)

    
class Cart(models.Model):
    class Meta:
        unique_together = (('order_id', 'prod_id'),)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    prod_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    def __str__(self):
        return str(self.prod_id + " " + self.quantity)
