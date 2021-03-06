from distutils.command.upload import upload
from itertools import product
import re
from django.db import models
from XHUser.models import XHUser
from xianhang.settings import BASE_URL, PI_URL

# Create your models here.
class Product(models.Model):

    # class TradingMethod(models.Model):
    #     class TradingChoice(models.IntegerChoices):
    #         DELI = 0, "Delivery"
    #         PICKUP = 1, "Pick up"

    #     meth = models.IntegerField(choices=TradingChoice.choices, unique=True)

    #     def __str__(self) -> str:
    #         return Product.TradingMethod.TradingChoice(self.meth).label

    #     def body(self):
    #         return {Product.TradingMethod.TradingChoice(self.meth) : Product.TradingMethod.TradingChoice(self.meth).label}

    class TradingMethod(models.IntegerChoices):
        DELI = 0, "Delivery"
        PICKUP = 1, "Pick Up"
        BOTH = 2, "Both"

    name = models.CharField(max_length=150, null=False, blank=False)
    description = models.CharField(max_length=150, null=False, blank=False)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    stock = models.IntegerField(default=1)
    user = models.ForeignKey(XHUser, on_delete=models.CASCADE, null=False, blank=False)
    tradingMethod = models.IntegerField(choices=TradingMethod.choices, default=0)
    pickUpLoc = models.CharField(max_length=150, default="", blank=True)

    def __str__(self) -> str:
        return self.name

    def body(self) -> dict: 
        return {
            'id' : self.id,
            'name' : self.name,
            'description' : self.description,
            'price' : self.price,
            'stock' : self.stock,
            'tradingMethod' : self.tradingMethod,
            'pickUpLoc' : self.pickUpLoc,
            'userId' : self.user.id,
            'username' : self.user.username,
        }

class ProductImage(models.Model):
    image = models.FileField(upload_to="productImage/")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, blank=False)

    @property
    def path(self) -> str:
        return PI_URL + self.image.name

    @property
    def ext(self) -> str:
        return self.image.name.split('.')[-1]