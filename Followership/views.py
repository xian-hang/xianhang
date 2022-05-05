import json
from django.shortcuts import render, get_object_or_404
from XHUser.models import XHUser
from common.validation import userIdValidation
from .models import Followership
from django.views.decorators.http import require_http_methods

from common.deco import user_logged_in
from common.functool import checkParameter, getReqUser
from common.restool import resBadRequest, resForbidden, resInvalidPara, resMissingPara, resOk, resReturn

# Create your views here.

@require_http_methods(['OPTIONS', 'POST'])
@user_logged_in
def createFollowership(request):
    if not checkParameter(['userId'], request):
        return resMissingPara(['userId'])

    data = json.loads(request.body)
    userId=data['userId']
    user = getReqUser(request)

    if userIdValidation(userId) and user.id != userId:
        following = XHUser.objects.get(id=userId)
        if not Followership.objects.filter(user=user, following=following).exists():
            followership = Followership.objects.create(user=user, following=following)
            return resReturn({'followershipId' : followership.id})
        else:
            return resBadRequest("Followership exists.")
    else:
        return resInvalidPara(["userId"])
    

@require_http_methods(['OPTIONS', 'DELETE'])
@user_logged_in
def deleteFollowership(request,id):
    user = getReqUser(request)
    followership = get_object_or_404(Followership, id=id)

    if user.id != followership.user.id:
        return resForbidden()

    followership.delete()
    return resOk()
    

@user_logged_in
def followershipList(request):
    user = getReqUser(request)
    followerships = Followership.objects.filter(user=user)
    return resReturn({"result" : [f.body() for f in followerships]})