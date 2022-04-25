
import json
from django.shortcuts import render,get_object_or_404
import os

from XHUser.models import XHUser
from .models import Product, ProductImage
from django.views.decorators.http import require_http_methods

from common.deco import check_logged_in, user_logged_in
from common.functool import checkParameter,getReqUser, pickUpAvailable, saveFormOr400
from common.validation import descriptionValidation, keywordValidation, nameValidation, pickUpLocValidation, productIdValidation, stockValidation, priceValidation, tradingMethodValidation
from common.restool import resBadRequest, resFile, resForbidden, resInvalidPara, resOk, resMissingPara, resReturn

from .form import ProductImageForm

# Create your views here.

@require_http_methods(['POST'])
@user_logged_in
def createProduct(request):
    user = XHUser.objects.get(username=request.user.username)
    if user.status == XHUser.StatChoice.RESTRT:
        return resForbidden("User is restricted.")

    if not checkParameter(["name","description","price","stock","tradingMethod"], request):
        return resMissingPara(["name","description","price","stock","tradingMethod"])

    data = json.loads(request.body)
    name = data['name']
    description = data['description']
    price = data['price']
    stock = data['stock']
    tradingMethod = data['tradingMethod']

    if nameValidation(name) and descriptionValidation(description) and priceValidation(price) and stockValidation(stock) and tradingMethodValidation(tradingMethod):
        if pickUpAvailable(tradingMethod):
            if "pickUpLoc" in data:
                pickUpLoc = data['pickUpLoc']
                if pickUpLocValidation(pickUpLoc):
                    product = Product.objects.create(name=name, description=description, price=price, stock=stock, user=user, tradingMethod=tradingMethod, pickUpLoc=pickUpLoc)
                else:
                    return resInvalidPara(["pickUpLoc"])
            else:
                return resMissingPara(["pickUpLoc"])
        else:
            product = Product.objects.create(name=name, description=description, price=price, stock=stock, user=user, tradingMethod=tradingMethod)
        return resReturn(product.body())
    else:
        return resInvalidPara(["name","description","price","stock","tradingMethod"])


def getProduct(request,id):
    product = get_object_or_404(Product, id=id)
    images = ProductImage.objects.filter(product=product)
    return resReturn({'product' : product.body(), 'image' : [i.id for i in images]})


@require_http_methods(['POST'])
@user_logged_in
def editProduct(request,id):
    reqUser = getReqUser(request)
    product = get_object_or_404(Product, id=id)

    if reqUser.id != product.user.id:
        return resForbidden()

    if not request.body:
        return resBadRequest("Empty parameter.")

    data = json.loads(request.body)
    updated = {}

    if "name" in data:
        name = data['name']
        if nameValidation(name):
            product.name = name
            updated = {**updated, 'name' : name}
        else:
            return resInvalidPara(["name"])

    if "description" in data:
        description = data['description']
        if descriptionValidation(description):
            product.description = description
            updated = {**updated, 'description' : description}
        else:
            return resInvalidPara(["description"])

    if "price" in data:
        price = data['price']
        if priceValidation(price):
            product.price = price
            updated = {**updated, 'price' : price}
        else:
            return resInvalidPara(["price"])

    if "stock" in data:
        stock = data['stock']
        if stockValidation(stock):
            product.stock = stock
            updated = {**updated, 'stock' : stock}
        else:
            return resInvalidPara(["stock"])

    if "tradingMethod" in data:
        tradingMethod = data['tradingMethod']
        if tradingMethodValidation(tradingMethod):
            product.tradingMethod = tradingMethod
            if pickUpAvailable(tradingMethod):
                if "pickUpLoc" in data:
                    pickUpLoc = data['pickUpLoc']
                    if pickUpLocValidation(pickUpLoc):
                        product.pickUpLoc = pickUpLoc
                        updated = {**updated, 'tradingMethod' : tradingMethod, 'pickUpLoc' : pickUpLoc}
                    else:
                        return resInvalidPara(["pickUpLoc"])
                else:
                    return resMissingPara(["pickUpLoc"])
            else:
                product.pickUpLoc = ""
                updated = {**updated, 'tradingMethod' : tradingMethod, 'pickUpLoc' : ""}
        else:
            return resInvalidPara(["tradingMethod"])

    product.save()
    return resReturn(updated)


@require_http_methods(['DELETE'])
@user_logged_in
def deleteProduct(request):
    reqUser = getReqUser(request)
    product = get_object_or_404(Product, id=id)

    if reqUser.id != product.user.id:
        return resForbidden()

    product.delete()
    return resOk()


@require_http_methods(['POST'])
def searchProduct(request):
    if not checkParameter(['keyword'], request):
        return resMissingPara(['keyword'])

    data = json.loads(request.body)
    keyword = data['keyword']

    if not keywordValidation(keyword):
        return resInvalidPara(["keyword"])

    products = Product.objects.filter(name__contains=keyword)
    
    results = []
    for p in products:
        images = ProductImage.objects.filter(product=p)
        results += [{'product' : p.body(), 'image' : [i.id for i in images]}]

    return resReturn(dict(results = results))


@require_http_methods(['POST'])
@user_logged_in
def createProductImage(request):
    user = getReqUser(request)

    if user.status == XHUser.StatChoice.RESTRT:
        return resForbidden("User is restricted")

    try:
        productId = int(request.POST.get('productId'))
    except:
        return resInvalidPara(['productId'])

    if not productIdValidation(productId):
        return resInvalidPara(['productId'])

    form = ProductImageForm(request.POST, request.FILES)
    image = saveFormOr400(form)
    image.product = Product.objects.get(id=productId)
    image.save()

    return resOk()


def getProductImage(request,id):
    image = get_object_or_404(ProductImage,id=id)
    return resFile(image.image)


@require_http_methods(['DELETE'])
@user_logged_in
def deleteProductImage(request,id):
    image = get_object_or_404(ProductImage,id=id)
    user = getReqUser(request)

    if user.id != image.product.user.id:
        return resForbidden()

    os.system("rm %s" % image.image.path)
    image.delete()

    return resOk()