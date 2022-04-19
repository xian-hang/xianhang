import json
from django.shortcuts import render,get_object_or_404

from XHUser.models import XHUser
from .models import Product
from django.views.decorators.http import require_http_methods

from common.deco import check_logged_in, user_logged_in
from common.functool import checkParameter,getReqUser
from common.validation import isString, keywordValidation, stockValidation, priceValidation
from common.restool import resOk, resError, resMissingPara, resReturn

# Create your views here.

@require_http_methods(['POST'])
@user_logged_in
def createProduct(request):
    user = XHUser.objects.get(username=request.user.username)
    if user.status == XHUser.StatChoices.RESTRT:
        return resError(403, "User is restricted.")

    if not checkParameter(["name","description","price","stock"], request):
        return resError(400)

    data = json.loads(request.body)
    name = data['name']
    description = data['description']
    price = data['price']
    stock = data['stock']
    if isString(name) and isString(description) and priceValidation(price) and stockValidation(stock):
        product = Product.objects.create(name=name, description=description, price=price, stock=stock, user=user)
        return resReturn(product.body())
    else:
        return resError(400)


def getProduct(request,id):
    product = get_object_or_404(Product, id=id)
    return resReturn(product.body())


@require_http_methods(['POST'])
@user_logged_in
def editProduct(request,id):
    reqUser = getReqUser(request)
    product = get_object_or_404(Product, id=id)

    if reqUser.id != product.user.id:
        return resError(403)

    if not request.body:
        return resOk()

    data = json.loads(request.body)
    updated = {}

    if "name" in data:
        name = data['name']
        if isString(name):
            product.name = name
            updated = {**updated, 'name' : name}
        else:
            return resError(400, "Invalid name.")

    if "description" in data:
        description = data['description']
        if isString(description):
            product.description = description
            updated = {**updated, 'description' : description}
        else:
            return resError(400, "Invalid description.")

    if "price" in data:
        price = data['price']
        if priceValidation(price):
            product.price = price
            updated = {**updated, 'price' : price}
        else:
            return resError(400, "Invalid price.")

    if "stock" in data:
        stock = data['stock']
        if stockValidation(stock):
            product.stock = stock
            updated = {**updated, 'stock' : stock}
        else:
            return resError(400, "Invalid stock.")

    product.save()
    return resReturn(updated)


@require_http_methods(['DELETE'])
@user_logged_in
def deleteProduct(request):
    reqUser = getReqUser(request)
    product = get_object_or_404(Product, id=id)

    if reqUser.id != product.user.id:
        return resError(403)

    product.delete()
    return resOk()


@require_http_methods(['POST'])
def searchProduct(request):
    if not checkParameter(['keyword'], request):
        return resMissingPara(['keyword'])

    data = json.loads(request.body)
    keyword = data['keyword']

    if not keywordValidation(keyword):
        return resError(400, "Invalid keyword.")

    products = Product.objects.filter(name__contains=keyword)
    return resReturn({"result" : [p.body() for p in products]})
