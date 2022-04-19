import re
from django.db import models
from XHUser.models import XHUser

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=150, null=False, blank=False)
    description = models.CharField(max_length=150, null=False, blank=False)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    stock = models.IntegerField(default=1)
    user = models.ForeignKey(XHUser, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self) -> str:
        return self.name

    def body(self) -> dict: 
        return {
            'id' : self.id,
            'name' : self.name,
            'description' : self.description,
            'price' : self.price,
            'stock' : self.stock,
            'user' : self.user.id,
        }
