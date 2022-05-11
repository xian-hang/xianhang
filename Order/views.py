from ast import Or
from gc import get_objects
from itertools import product
import json
from math import prod
from django.shortcuts import render, get_object_or_404
from Product.models import Product

from common.restool import resBadRequest, resForbidden, resInvalidPara, resMissingPara, resOk, resReturn, resUnauthorized
from .models import Order
from django.views.decorators.http import require_http_methods

from common.deco import user_logged_in
from common.functool import by_date, checkParameter, getFirstProductImageId, getReqUser, pickUpAvailable
from common.validation import deliveringAddrValidation, orderStatusValidation, pickedTradingMethodValidation, postageValidation, priceValidation, amountValidation, productIdValidation, nameValidation, phoneNumValidation

# Create your views here.
@require_http_methods(['OPTIONS', 'POST'])
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
        return resBadRequest("用户不可以买自己售卖的商品")
    
    if amount > product.stock:
        return resBadRequest("购买数量不可大于库存量")

    if tradingMethod == Order.TradingMethod.PICKUP:
        if not pickUpAvailable(product.tradingMethod):
            return resForbidden("商品不可自取")

        order = Order.objects.create(price=price, postage=0, amount=amount, product=product, user=user, name=name, phoneNum=phoneNum, tradingMethod=tradingMethod, pname=product.name, seller=product.user)
        product.stock -= amount
        product.save()
        return resReturn({'orderId' : order.id})
    else:
        if not checkParameter(['deliveringAddr'], request):
            return resMissingPara(['deliveringAddr'])
            
        addr = data['deliveringAddr']
        if not deliveringAddrValidation(addr):
            return resInvalidPara(['deliveringAddr'])

        order = Order.objects.create(price=price, amount=amount, product=product, user=user, name=name, phoneNum=phoneNum, tradingMethod=tradingMethod, deliveringAddr=addr, pname=product.name, seller=product.user)
        product.stock -= amount
        product.save()
        return resReturn({'orderId' : order.id})


@user_logged_in
def getOrder(request,id):
    order = get_object_or_404(Order, id=id)
    user = getReqUser(request)

    if user is None:
        return resUnauthorized("用户未登录")

    if user.id != order.user.id and user.id != order.product.user.id:
        return resForbidden("该订单与您不相关")

    return resReturn({'order' : order.body()})


@require_http_methods(['OPTIONS', 'POST'])
@user_logged_in
def editOrder(request,id):
    order = get_object_or_404(Order, id=id)
    user = getReqUser(request)

    if user.id != order.user.id:
        return resForbidden()

    if not request.body:
        return resBadRequest("Empty parameter.")

    if order.status not in [Order.StatChoice.UNPAID, Order.StatChoice.PAID]:
        return resForbidden("订单已不允许更改")

    data = json.loads(request.body)
    # updated = {}

    if "name" in data:
        name = data['name']
        if nameValidation(name):
            order.name = name
            # updated = {**updated, 'name' : name}
        else:
            return resInvalidPara(['name'])

    if "phoneNum" in data:
        phoneNum = data['phoneNum']
        if phoneNumValidation(phoneNum):
            order.phoneNum = phoneNum
            # updated = {**updated, 'phoneNum' : phoneNum}
        else:
            return resInvalidPara(['name'])


    if "tradingMethod" in data:
        tradingMethod = data['tradingMethod']
        if not pickedTradingMethodValidation(tradingMethod):
            return resInvalidPara(['tradingMethod'])

        if tradingMethod == Order.TradingMethod.PICKUP:
            if not pickUpAvailable(order.product.tradingMethod):
                return resForbidden("该商品不可自取")

            order.tradingMethod = tradingMethod
            order.deliveringAddr = None
            # updated = {**updated, 'tradingMethod' : tradingMethod, 'deliveringAddr' : None}

        else:
            if not checkParameter(['deliveringAddr'],request):
                return resMissingPara(['deliveringAddr'])

            addr = data['deliveringAddr']
            if deliveringAddrValidation(addr):
                order.tradingMethod = tradingMethod
                order.deliveringAddr = addr
                # updated = {**updated, 'tradingMethod' : tradingMethod, 'deliveringAddr' : addr}
            else:
                return resInvalidPara(['deliveringAddr'])


    order.save()
    return resOk()


@require_http_methods(['OPTIONS', 'POST'])
@user_logged_in
def editOrderStatus(request,id):
    order = get_object_or_404(Order, id=id)
    user = getReqUser(request)

    if not checkParameter(['status'], request):
        return resMissingPara(['status'])
    
    data = json.loads(request.body)
    status = data['status']
    if not orderStatusValidation(status):
        return resInvalidPara(['status'])

    if user.id == order.user.id:
        if status == Order.StatChoice.PAID:
            if order.status == Order.StatChoice.UNPAID:
                if order.tradingMethod == order.TradingMethod.DELI and order.postage is None:
                    return resBadRequest("邮费还未确认")
            
                order.status = status
                if order.tradingMethod == order.TradingMethod.PICKUP:
                    order.status = order.StatChoice.SHP
                order.save()

                seller = order.product.user
                seller.soldItem += order.amount
                seller.save()
                return resOk("Order's status is changed from %s to %s." % (Order.StatChoice.UNPAID.label,Order.StatChoice(order.status).label))

        elif status == Order.StatChoice.COMP:
            if order.status == order.StatChoice.SHP:
                order.status = status
                order.save()
                return resOk("Order's status is changed from %s to %s." % (Order.StatChoice.SHP.label,Order.StatChoice(order.status).label))

        elif status == Order.StatChoice.CANC:
            if order.status == order.StatChoice.UNPAID:
                order.status = status
                order.save()
                
                product = order.product
                product.stock += order.amount
                product.save()
                return resOk("Order's status is changed from %s to %s." % (Order.StatChoice.UNPAID.label,Order.StatChoice(order.status).label))

    elif user.id == order.product.user.id:
        if status == Order.StatChoice.SHP:
            if order.status == Order.StatChoice.PAID:
                order.status = status
                order.save()
                return resOk("Order's status is changed from %s to %s." % (Order.StatChoice.PAID.label,Order.StatChoice(order.status).label))
    
    else:
        return resForbidden("User is not allowed to edit order's status.")

    
    return resBadRequest("User is not allowed to change order's status from %s to %s." % (Order.StatChoice(order.status).label,Order.StatChoice(status).label))
    

@require_http_methods(['OPTIONS', 'POST'])
@user_logged_in
def editOrderPostage(request, id): 
    user = getReqUser(request)
    order = get_object_or_404(Order, id=id)

    if user is None:
        return resUnauthorized("用户未登录")

    if user.id != order.product.user.id or order.tradingMethod != Order.TradingMethod.DELI or order.postage != None:
        return resForbidden("只有商家可以设置邮费")

    if not checkParameter(['postage'], request):
        return resMissingPara(['postage'])
    
    data = json.loads(request.body)
    postage = data['postage']

    if not postageValidation(postage):
        return resInvalidPara(['postage'])

    order.postage = postage
    order.save()
    return resOk()

@user_logged_in
def sellingList(request):
    user = getReqUser(request)
    orders = Order.objects.filter(seller=user).order_by('-id')
    return resReturn({"result" : [{'order' : o.body(), 'image' : getFirstProductImageId(o.product)} for o in orders]})


@require_http_methods(['OPTIONS', 'POST'])
@user_logged_in
def sellingListWithStatus(request):
    if not checkParameter(['status'],request):
        return resMissingPara(['status'])

    data = json.loads(request.body)
    status = data['status']
    if not orderStatusValidation(status):
        return resInvalidPara(['status'])

    user = getReqUser(request)
    orders = Order.objects.filter(seller=user,status=status).order_by('-id')
    return resReturn({"result" : [{'order' : o.body(), 'image' : getFirstProductImageId(o.product)} for o in orders]})


@user_logged_in
def buyingList(request):
    user = getReqUser(request)
    orders = Order.objects.filter(user=user).order_by('-id')
    return resReturn({"result" : [{'order' : o.body(), 'image' : getFirstProductImageId(o.product)} for o in orders]})


@require_http_methods(['OPTIONS', 'POST'])
@user_logged_in
def buyingListWithStatus(request):
    if not checkParameter(['status'],request):
        return resMissingPara(['status'])

    data = json.loads(request.body)
    status = data['status']
    if not orderStatusValidation(status):
        return resInvalidPara(['status'])

    user = getReqUser(request)
    orders = Order.objects.filter(user=user,status=status).order_by('-id')
    return resReturn({"result" : [{'order' : o.body(), 'image' : getFirstProductImageId(o.product)} for o in orders]})