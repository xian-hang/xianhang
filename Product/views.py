import json
from django.shortcuts import render

from XHUser.models import XHUser
from .models import Product
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods

from xianhang.deco import check_logged_in, user_logged_in
from xianhang.functool import checkParameter, isFloat, isInt, isString

# Create your views here.

@require_http_methods(['POST'])
@user_logged_in
def createProduct(request):
    user = XHUser.objects.get(username=request.user.username)
    if user.status == XHUser.StatChoices.RESTRT:
        return HttpResponse(status=403)

    if not checkParameter(["name","description","price","stock"], request):
        return HttpResponse(status=400)

    data = json.loads(request.body)
    name = data['name']
    description = data['description']
    price = data['price']
    stock = data['stock']
    if isString(name) and isString(description) and isFloat(price) and isInt(stock):
        product = Product.objects.create(name=name, description=description, price=price, stock=stock, user=user)
        return JsonResponse(product.body())
    else:
        return HttpResponse(status=400)


def product(request,id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return HttpResponse(status=404)

    return JsonResponse(product.body())


@require_http_methods(['POST','DELETE'])
@check_logged_in
def editProduct(request,id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'POST':
        changed = {}

        if request.body:
            data = json.loads(request.body)

            if "name" in data:
                name = data['name']
                if isString(name):
                    product.name = name
                    changed = {**changed, 'name' : name}
                else:
                    return HttpResponse(status=400)

            if "description" in data:
                description = data['description']
                if isString(description):
                    product.description = description
                    changed = {**changed, 'description' : description}
                else:
                    return HttpResponse(status=400)

            if "price" in data:
                price = data['price']
                if isFloat(price):
                    product.price = price
                    changed = {**changed, 'price' : price}
                else:
                    return HttpResponse(status=400)

            if "stock" in data:
                stock = data['stock']
                if isInt(data['stock']):
                    product.stock = stock
                    changed = {**changed, 'stock' : stock}
                else:
                    return HttpResponse(status=400)

            product.save()
            return JsonResponse(changed)

    elif request.method == 'DELETE':
        product.delete()
        return HttpResponse()

