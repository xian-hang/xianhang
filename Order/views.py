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
from common.functool import checkParameter, getFirstProductImageId, getReqUser, pickUpAvailable
from common.validation import deliveringAddrValidation, orderStatusValidation, pickedTradingMethodValidation, priceValidation, amountValidation, productIdValidation, nameValidation, phoneNumValidation

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
    
    if amount > product.stock:
        return resBadRequest("Purchase amount exceeds stock no.")

    if tradingMethod == Order.TradingMethod.PICKUP:
        if not pickUpAvailable(product.tradingMethod):
            return resForbidden("Product is not allowed for pick up.")

        Order.objects.create(price=price, postage=0, amount=amount, product=product, user=user, name=name, phoneNum=phoneNum, tradingMethod=tradingMethod)
        product.stock -= amount
        product.save()
        return resOk()
    else:
        if not checkParameter(['deliveringAddr'], request):
            return resMissingPara(['deliveringAddr'])
            
        addr = data['deliveringAddr']
        if not deliveringAddrValidation(addr):
            return resInvalidPara(['deliveringAddr'])

        Order.objects.create(price=price, amount=amount, product=product, user=user, name=name, phoneNum=phoneNum, tradingMethod=tradingMethod, deliveringAddr=addr)
        product.stock -= amount
        product.save()
        return resOk()


@user_logged_in
def getOrder(request,id):
    order = get_object_or_404(Order, id=id)
    user = getReqUser(request)

    if user.id != order.user.id and user.id != order.product.user.id:
        return resForbidden()

    return resReturn(order.body())


@require_http_methods(['POST'])
@user_logged_in
def editOrder(request,id):
    order = get_object_or_404(Order, id=id)
    user = getReqUser(request)

    if user.id != order.user.id:
        return resForbidden()

    if not request.body:
        return resBadRequest("Empty parameter.")

    if order.status not in [Order.StatChoice.UNPAID, Order.StatChoice.PAID]:
        return resForbidden("Order is not allowed to be modified anymore.")

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
                return resForbidden("Product is not allowed for pick up.")

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


@require_http_methods(['POST'])
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
                    return resBadRequest("Postage is not confirmed yet.")
            
                order.status = status
                if order.tradingMethod == order.TradingMethod.PICKUP:
                    order.status = order.StatChoice.SHP
                order.save()

                user.soldItem += order.amount
                user.save()
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
    

@user_logged_in
def sellingList(request):
    user = getReqUser(request)
    products = user.product_set.all()
    orders = set()
    for p in products:
        orders |= set(p.order_set.all())

    return resReturn({"result" : [{'order' : o.body(), 'image' : getFirstProductImageId(o.product)} for o in orders]})


@user_logged_in
def sellingListWithStatus(request):
    if not checkParameter(['status'],request):
        return resMissingPara(['status'])

    data = json.loads(request.body)
    status = data['status']
    if not orderStatusValidation(status):
        return resInvalidPara(['status'])

    user = getReqUser(request)
    products = user.product_set.all()
    orders = set()
    for p in products:
        orders |= set(p.order_set.filter(status=status))

    return resReturn({"result" : [{'order' : o.body(), 'image' : getFirstProductImageId(o.product)} for o in orders]})


@user_logged_in
def buyingList(request):
    user = getReqUser(request)
    orders = user.order_set.all()

    return resReturn({"result" : [{'order' : o.body(), 'image' : getFirstProductImageId(o.product)} for o in orders]})


@user_logged_in
def buyingListWithStatus(request):
    if not checkParameter(['status'],request):
        return resMissingPara(['status'])

    data = json.loads(request.body)
    status = data['status']
    if not orderStatusValidation(status):
        return resInvalidPara(['status'])

    user = getReqUser(request)
    orders = user.order_set.filter(status=status)

    return resReturn({"result" : [{'order' : o.body(), 'image' : getFirstProductImageId(o.product)} for o in orders]})