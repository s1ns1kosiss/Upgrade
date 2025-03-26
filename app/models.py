from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100,blank=False,null=False,default="")
    brand = models.CharField(max_length=50,default="")
    price = models.IntegerField()
    description = models.TextField()
    image = models.URLField()
    rating=models.DecimalField(max_digits=2, decimal_places=1)
    quantity=models.IntegerField(default=1)
    stock=models.IntegerField(default=1)

    def __str__(self):
        return self.name
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    address=models.CharField(max_length=100,blank=True,null=True,default="")
    addressNro=models.CharField(max_length=100,blank=True,null=True,default="")
    status = models.CharField(max_length=20, default='Pending') 
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f'Order {self.id} by {self.user.username}'

class OrderDetail(models.Model):
    order = models.ForeignKey(Order, related_name='details', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.product.name} (Order {self.order.id})'

    def get_total_price(self):
        return self.quantity * self.price