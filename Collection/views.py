from itertools import product
import json
from django.shortcuts import render, get_object_or_404
from XHUser.models import XHUser
from Product.models import Product
from common.validation import productIdValidation
from .models import Collection
from django.views.decorators.http import require_http_methods

from common.deco import user_logged_in
from common.functool import checkParameter, getReqUser
from common.restool import resError, resInvalidPara, resMissingPara, resOk, resReturn

# Create your views here.

@require_http_methods(['POST'])
@user_logged_in
def createCollection(request):
    if not checkParameter(['productId'], request):
        return resMissingPara(['productId'])

    data = json.loads(request.body)
    productId=data['productId']

    if productIdValidation(productId):
        user = getReqUser(request)
        product = Product.objects.get(id=productId)
        if not Collection.objects.filter(user=user, product=product).exists():
            collection = Collection.objects.create(user=user, product=product)
            return resOk()
        else:
            return resError(400, "Collection exists.")
    else:
        return resInvalidPara(["productId"])
    

@require_http_methods(['DELETE'])
@user_logged_in
def deleteCollection(request,id):
    user = getReqUser(request)
    collection = get_object_or_404(Collection, id=id)

    if user.id != collection.user.id:
        return resError(403)

    collection.delete()
    return resOk()
    

@user_logged_in
def collectionList(request):
    user = getReqUser(request)
    collections = Collection.objects.filter(user=user)
    return resReturn({"result" : [c.product.body() for c in collections]})