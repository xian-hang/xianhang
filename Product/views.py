import json
from django.shortcuts import render

from XHUser.models import XHUser
from .models import Product
from django.views.decorators.http import require_http_methods

from common.deco import check_logged_in, user_logged_in
from common.functool import checkParameter
from common.validation import isFloat, isInt, isString
from common.restool import resOk, resError, resMissingPara, resReturn

# Create your views here.

@require_http_methods(['POST'])
@user_logged_in
def createProduct(request):
    user = XHUser.objects.get(username=request.user.username)
    if user.status == XHUser.StatChoices.RESTRT:
        return resError(403)

    if not checkParameter(["name","description","price","stock"], request):
        return resError(400)

    data = json.loads(request.body)
    name = data['name']
    description = data['description']
    price = data['price']
    stock = data['stock']
    if isString(name) and isString(description) and isFloat(price) and isInt(stock):
        product = Product.objects.create(name=name, description=description, price=price, stock=stock, user=user)
        return resReturn(product.body())
    else:
        return resError(400)


def product(request,id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return resError(404)

    return resReturn(product.body())


@require_http_methods(['POST','DELETE'])
@check_logged_in
def editProduct(request,id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return resError(404)

    if request.method == 'POST':
        updated = {}

        if request.body:
            data = json.loads(request.body)

            if "name" in data:
                name = data['name']
                if isString(name):
                    product.name = name
                    updated = {**updated, 'name' : name}
                else:
                    return resError(400)

            if "description" in data:
                description = data['description']
                if isString(description):
                    product.description = description
                    updated = {**updated, 'description' : description}
                else:
                    return resError(400)

            if "price" in data:
                price = data['price']
                if isFloat(price):
                    product.price = price
                    updated = {**updated, 'price' : price}
                else:
                    return resError(400)

            if "stock" in data:
                stock = data['stock']
                if isInt(data['stock']):
                    product.stock = stock
                    updated = {**updated, 'stock' : stock}
                else:
                    return resError(400)

            product.save()
            return resReturn(updated)

    elif request.method == 'DELETE':
        product.delete()
        return resOk()

