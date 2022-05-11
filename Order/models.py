from django.db import models
from Product.models import Product

from XHUser.models import XHUser

# Create your models here.

class Order(models.Model):
    class StatChoice(models.IntegerChoices):
        UNPAID = 0, "Unpaid" # 待付款
        PAID = 1, "Paid" # 待发货
        SHP = 2, "Shipped" # 待收货
        COMP = 3, "Completed" # 已完成
        CANC = 4, "Cancelled" # 已取消

    class TradingMethod(models.IntegerChoices):
        DELI = 0, "Delivery"
        PICKUP = 1, "PickUp"

    price = models.DecimalField(decimal_places=2, max_digits=10)
    postage = models.DecimalField(decimal_places=2, max_digits=10, default=None, null=True)
    amount = models.IntegerField(default=1)
    status = models.IntegerField(choices=StatChoice.choices, default=0)
    user = models.ForeignKey(XHUser, on_delete=models.SET_NULL, null=True, related_name="creatingOrderUser")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    pname = models.CharField(max_length=150, null=True)
    seller = models.ForeignKey(XHUser, on_delete=models.CASCADE, null=True, related_name="seller")
    createdAt = models.DateTimeField(auto_now_add=True) 

    name = models.CharField(max_length=150, null=False, blank=False)
    phoneNum = models.CharField(max_length=11, null=False, blank=False)
    tradingMethod = models.IntegerField(choices=TradingMethod.choices, default=0)
    deliveringAddr = models.CharField(max_length=150, default=None, null=True, blank=True)

    def body(self) -> dict:
        return {
            'id' : self.id,
            'price' : self.price,
            'postage' : self.postage,
            'amount' : self.amount,
            'status' : self.status,
            'product' : self.product.body() if self.product else None,
            'pname' : self.pname,
            'sellerId' : self.seller.id if self.seller else None,
            'user' : self.user.id if self.user else None,
            'name' : self.name,
            'phoneNum' : self.phoneNum,
            'tradingMethod' : self.tradingMethod,
            'deliveringAddr' : self.deliveringAddr,
        }