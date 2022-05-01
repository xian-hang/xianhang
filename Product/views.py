
import json
from django.shortcuts import render,get_object_or_404
import os
import requests

from XHUser.models import XHUser
from .models import Product, ProductImage
from django.views.decorators.http import require_http_methods

from common.deco import check_logged_in, user_logged_in
from common.functool import checkParameter, getFirstProductImageId,getReqUser, pickUpAvailable, saveFormOr400
from common.validation import descriptionValidation, keywordValidation, nameValidation, pickUpLocValidation, productIdValidation, stockValidation, priceValidation, tradingMethodValidation
from common.restool import resBadRequest, resFile, resForbidden, resImage, resInvalidPara, resOk, resMissingPara, resReturn
import boto3
from xianhang.settings import AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY,S3_BUCKET, MEDIA_URL, PI_URL

from .form import ProductImageForm

# Create your views here.

@require_http_methods(['POST'])
@user_logged_in
def createProduct(request):
    user = getReqUser(request)
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
    # updated = {}

    if "name" in data:
        name = data['name']
        if nameValidation(name):
            product.name = name
            # updated = {**updated, 'name' : name}
        else:
            return resInvalidPara(["name"])

    if "description" in data:
        description = data['description']
        if descriptionValidation(description):
            product.description = description
            # updated = {**updated, 'description' : description}
        else:
            return resInvalidPara(["description"])

    if "price" in data:
        price = data['price']
        if priceValidation(price):
            product.price = price
            # updated = {**updated, 'price' : price}
        else:
            return resInvalidPara(["price"])

    if "stock" in data:
        stock = data['stock']
        if stockValidation(stock):
            product.stock = stock
            # updated = {**updated, 'stock' : stock}
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
                        # updated = {**updated, 'tradingMethod' : tradingMethod, 'pickUpLoc' : pickUpLoc}
                    else:
                        return resInvalidPara(["pickUpLoc"])
                else:
                    return resMissingPara(["pickUpLoc"])
            else:
                product.pickUpLoc = ""
                # updated = {**updated, 'tradingMethod' : tradingMethod, 'pickUpLoc' : ""}
        else:
            return resInvalidPara(["tradingMethod"])

    product.save()
    return resOk()


@require_http_methods(['DELETE'])
@user_logged_in
def deleteProduct(request, id):
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

    products = Product.objects.filter(name__icontains=keyword)
    return resReturn({'result' : [{'product' : p.body(), 'image' : getFirstProductImageId(p)} for p in products]})

def allProduct(request):
    products = set(Product.objects.exclude(stock=0))
    user = getReqUser(request)
    if user is not None:
        products -= set(Product.objects.filter(user=user))
    return resReturn({'result' : [{'product' : p.body(), 'image' : getFirstProductImageId(p)} for p in products]})

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

    # print(type(request.FILES['image'].file))
    form = ProductImageForm(request.POST, request.FILES)
    if not form.is_valid():
        return resBadRequest("Form invalid.")

    product = Product.objects.get(id=productId)
    image = ProductImage.objects.create(product=product)
    image.image = str(image.id) + "_" + request.FILES['image'].name
    image.save()

    imData = request.FILES['image']
    s3 = boto3.resource('s3',aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key= AWS_SECRET_ACCESS_KEY)
    obj = s3.Object('xianhang-bucket', MEDIA_URL + PI_URL + image.image.name)
    r = obj.put(Body=imData)
    print(r)

    return resOk()


def getProductImage(request,id):
    image = get_object_or_404(ProductImage,id=id)

    s3_client = boto3.client('s3',aws_access_key_id=AWS_ACCESS_KEY_ID,
         aws_secret_access_key= AWS_SECRET_ACCESS_KEY)
    response = s3_client.generate_presigned_url('get_object',
                                                Params={'Bucket': 'xianhang-bucket',
                                                        'Key': MEDIA_URL + PI_URL + image.image.name},
                                                ExpiresIn=3000)
    r = requests.get(response)
    ext = image.image.name.split('.')[-1]
    return resImage(r,ext)


@require_http_methods(['DELETE'])
@user_logged_in
def deleteProductImage(request,id):
    image = get_object_or_404(ProductImage,id=id)
    user = getReqUser(request)

    if user.id != image.product.user.id:
        return resForbidden()

    s3 = boto3.resource('s3',aws_access_key_id=AWS_ACCESS_KEY_ID,
         aws_secret_access_key= AWS_SECRET_ACCESS_KEY)
    obj = s3.Object('xianhang-bucket', MEDIA_URL + PI_URL + image.image.name)
    r = obj.delete()

    image.delete()

    return resOk()


@user_logged_in
def getFeed(request):
    user = getReqUser(request)
    followingId = user.creatingFollowershipUser.values_list('following__id')
    users = XHUser.objects.filter(id__in=followingId)
    products = Product.objects.filter(user__in=users)
    return resReturn({'result' : [{'product' : p.body(), 'image': getFirstProductImageId(p)} for p in products]})