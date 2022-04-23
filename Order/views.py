from ast import Or
from gc import get_objects
import json
from math import prod
from django.shortcuts import render, get_object_or_404
from Product.models import Product

from common.restool import resBadRequest, resForbidden, resInvalidPara, resMissingPara, resOk, resReturn
from .models import Order
from django.views.decorators.http import require_http_methods

from common.deco import user_logged_in
from common.functool import checkParameter, getReqUser, pickUpChosen
from common.validation import deliveringAddrValidation, pickedTradingMethodValidation, priceValidation, amountValidation, productIdValidation, nameValidation, phoneNumValidation

# Create your views here.
@require_http_methods(['POST'])
@user_logged_in
def createOrder(request):
    if not checkParameter(['price', 'amount', 'productId', 'name', 'phoneNum', 'tradingMethod'], request):
        return resMissingPara(['price', 'amount', 'productId', 'name', 'phoneNum', 'tradingMethod'])

    data = json.loads(request.body)
    price = data['price']
    amount = data['amount']
    productId = data['productId']
    name = data['name']
    phoneNum = data['phoneNum']
    tradingMethod = data['tradingMethod']
    
    if not (priceValidation(price) and amountValidation(amount)  and productIdValidation(productId) and nameValidation(name) and phoneNumValidation(phoneNum) and pickedTradingMethodValidation(tradingMethod)):
        return resInvalidPara(['price', 'amount', 'productId', 'name', 'phoneNum', 'tradingMethod'])

    user = getReqUser(request)
    product = Product.objects.get(id=productId)
    if user.id == product.user.id:
        return resBadRequest("Product belongs to user.")

    if pickUpChosen(tradingMethod):
        Order.objects.create(price=price, postage=0, amount=amount, product=product, user=user, name=name, phoneNum=phoneNum, tradingMethod=tradingMethod)
        return resOk()
    else:
        if not checkParameter(['deliveringAddr'], request):
            return resMissingPara(['deliveringAddr'])
            
        addr = data['deliveringAddr']
        if not deliveringAddrValidation(addr):
            return resInvalidPara(['deliveringAddr'])

        Order.objects.create(price=price, amount=amount, product=product, user=user, name=name, phoneNum=phoneNum, tradingMethod=tradingMethod, deliveringAddr=addr)
        return resOk()


@user_logged_in
def getOrder(request,id):
    order = get_object_or_404(Order, id=id)
    user = getReqUser(request)

    if user.id != order.user.id and user.id != order.product.user.id:
        return resForbidden()

    return resReturn(order.body())


@user_logged_in
def editOrder(request,id):
    order = get_object_or_404(Order, id=id)
    user = getReqUser(request)

    if user.id != order.user.id:
        return resForbidden()

    if not request.body:
        return resBadRequest("Empty parameter.")

    if order.status in [Order.StatChoice.UNPAID, Order.StatChoice.PAID]:
        return resBadRequest("Order is not allowed to be modified anymore.")

    data = json.loads(request.body)
    updated = {}

    if "name" in data:
        name = data['name']
        if nameValidation(name):
            order.name = name
            updated = {**updated, 'name' : name}
        else:
            return resInvalidPara(['name'])

    if "phoneNum" in data:
        phoneNum = data['phoneNum']
        if phoneNumValidation(phoneNum):
            order.phoneNum = phoneNum
            updated = {**updated, 'phoneNum' : phoneNum}
        else:
            return resInvalidPara(['name'])


    if "tradingMethod" in data:
        tradingMethod = data['tradingMethod']
        if not pickedTradingMethodValidation(tradingMethod):
            return resInvalidPara(['tradingMethod'])

        if tradingMethod == Order.TradingMethod.PICKUP:
            order.tradingMethod = tradingMethod
            order.deliveringAddr = ""
            updated = {**updated, 'tradingMethod' : tradingMethod, 'deliveringAddr' : ""}
        else:
            if not checkParameter(['deliveringAddr']):
                return resMissingPara(['deliveringAddr'])

            addr = data['deliveringAddr']
            if deliveringAddrValidation(addr):
                order.tradingMethod = tradingMethod
                order.deliveringAddr = addr
                updated = {**updated, 'tradingMethod' : tradingMethod, 'deliveringAddr' : addr}
            else:
                return resInvalidPara(['deliveringAddr'])


    order.save()
    return resReturn(updated)


@require_http_methods(['POST'])
@user_logged_in
def editOrderStatus(request,id):
    order = get_object_or_404(Order, id=id)
    user = getReqUser(request)

    if user.id == order.user.id:
        pass
    elif user.id == order.product.user.id:
        pass
    else:
        return resForbidden()
    

    