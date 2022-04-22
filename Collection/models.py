from django.db import models
from XHUser.models import XHUser
from Product.models import Product
# Create your models here.

class Collection(models.Model):
    user = models.ForeignKey(XHUser, null=False, blank=False, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=False, blank=False, on_delete=models.CASCADE)