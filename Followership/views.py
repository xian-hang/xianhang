import json
from django.shortcuts import render, get_object_or_404
from XHUser.models import XHUser
from common.validation import userIdValidation
from .models import Followership
from django.views.decorators.http import require_http_methods

from common.deco import user_logged_in
from common.functool import checkParameter, getReqUser
from common.restool import resBadRequest, resForbidden, resInvalidPara, resMissingPara, resOk, resReturn, resUnauthorized

# Create your views here.

@require_http_methods(['OPTIONS', 'POST'])
@user_logged_in
def createFollowership(request):
    if not checkParameter(['userId'], request):
        return resMissingPara(['userId'])

    data = json.loads(request.body)
    userId = data['userId']
    user = getReqUser(request)

    if userIdValidation(userId):
        return resInvalidPara(["userId"])
    if user.id == userId:
        return resForbidden("不可自己关注自己")
    following = XHUser.objects.get(id=userId)
    if not Followership.objects.filter(user=user, following=following).exists():
        followership = Followership.objects.create(user=user, following=following)
        return resReturn({'followershipId' : followership.id})
    else:
        return resBadRequest("Followership exists.")


@require_http_methods(['OPTIONS', 'DELETE'])
@user_logged_in
def deleteFollowership(request,id):
    user = getReqUser(request)
    followership = get_object_or_404(Followership, id=id)

    if user.id != followership.user.id:
        return resForbidden("关注关系不相关")

    followership.delete()
    return resOk()
    

@user_logged_in
def followershipList(request):
    user = getReqUser(request)
    if user is None: 
        return resUnauthorized("用户未登录")
    followerships = Followership.objects.filter(user=user)
    return resReturn({"result" : [f.body() for f in followerships]})