import json
from django.shortcuts import render, get_object_or_404
from XHUser.models import XHUser
from Product.models import Product
from common.validation import productIdValidation
from .models import Collection
from django.views.decorators.http import require_http_methods

from common.deco import user_logged_in
from common.functool import checkParameter, getFirstProductImageId, getReqUser
from common.restool import resBadRequest, resForbidden, resInvalidPara, resMissingPara, resOk, resReturn, resUnauthorized

# Create your views here.

@require_http_methods(['OPTIONS', 'POST'])
@user_logged_in
def createCollection(request):
    if not checkParameter(['productId'], request):
        return resMissingPara(['productId'])

    data = json.loads(request.body)
    productId = data['productId']

    if productIdValidation(productId):
        user = getReqUser(request)
        if user is None:
            return resUnauthorized("用户未登录")
        product = Product.objects.get(id=productId)
        if not Collection.objects.filter(user=user, product=product).exists():
            collection = Collection.objects.create(user=user, product=product)
            return resReturn({'collectionId' : collection.id})
        else:
            return resBadRequest("该商品已收藏过")
    else:
        return resInvalidPara(["productId"])
    

@require_http_methods(['OPTIONS', 'DELETE'])
@user_logged_in
def deleteCollection(request,id):
    user = getReqUser(request)
    if user is None:
        return resUnauthorized("用户未登录")
    collection = get_object_or_404(Collection, id=id)

    if user.id != collection.user.id:
        return resForbidden("不可删除其他用户的收藏")

    collection.delete()
    return resOk()
    

@user_logged_in
def collectionList(request):
    user = getReqUser(request)
    if user is None:
        return resUnauthorized("用户未登录")
    collections = Collection.objects.filter(user=user)
    return resReturn({"result" : [{'product' : c.product.body(), 'image' : getFirstProductImageId(c.product)} for c in collections]})