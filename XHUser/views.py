import json
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, logout
from Product.views import product
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404

from xianhang.settings import EMAIL_HOST_USER
from .models import XHUser
from Product.models import Product
from common.deco import admin_logged_in, check_logged_in
from common.functool import checkParameter, getActiveUser, getReqUser, getObjectOrResError
from common.validation import isInt, isString, passwordValidation, usernameValidation 
from common.restool import resError, resMissingPara, resOk, resReturn
from common.mail import mailtest, sendVerificationMail

# Create your views here.
def checkReq(request):
    print(getActiveUser(id=17))
    # print(request.META)
    return resOk()



def sendEmailTest(request):
    # data = json.loads(request.body)
    mailtest()
    return resOk()


@require_http_methods(["POST"])
def userLogin(request):
    if not checkParameter(['studentId', 'password'], request):
        return resMissingPara(['studentId', 'password'])

    data = json.loads(request.body)
    studentId = data['studentId']
    password = data['password']

    if not isString(studentId) or not isString(password):
        return resError(401)

    try:
        user = XHUser.objects.get(studentId=studentId)
    except:
        return resError(401)

    if user.role == XHUser.RoleChoices.ADMIN:
        if user.check_password(data['password']):
            login(request,user)
            token, created = Token.objects.get_or_create(user=user)
            return resReturn({
                'role': 'admin',
                'token': token.key
            })
    elif user.status in [XHUser.StatChoices.VER, XHUser.StatChoices.RESTRT]:
        if user.check_password(password):
            login(request,user)
            token, created = Token.objects.get_or_create(user=user)
            print(token)
            return resReturn({
                'role': 'user',
                'token': token.key
            })

    return resError(401)


@require_http_methods(["POST"])
@check_logged_in
def userLogout(request):
    user = getReqUser(request)
    Token.objects.filter(user=user).delete()
    logout(request)
    return resOk()


@require_http_methods(["POST"])
def createUser(request):
    if not checkParameter(['username', 'studentId', 'password'], request):
        return resMissingPara(['username', 'studentId', 'password'])

    data = json.loads(request.body)
    username = data['username']
    studentId = data['studentId']
    password = data['password']

    if not usernameValidation(username) or not passwordValidation(password) or not isString(studentId):
        return resError(400, "Invalid username, studentId or password.")

    if XHUser.objects.filter(studentId=studentId).exists():
        return resError(403, "Given student id exists.")
    
    if XHUser.objects.filter(username=username).exists():
        return resError(403, "Given username exists.")

    user = XHUser.objects.create(username=username,
                                 studentId=studentId)
    user.set_password(password)
    user.save()
    # token = Token.objects.create(user=user)

    sendVerificationMail(user.id, studentId, username)

    return resOk({'message': 'email sent'})


def verifyEmail(request, id):
    user = get_object_or_404(XHUser,id=id)
    if user.status != XHUser.StatChoices.UNVER:
        return resError(403)
    user.status = XHUser.StatChoices.VER
    user.save()
    return resOk({'message': 'email verified'})


def user(request, id):
    user = get_object_or_404(XHUser,id=id)
    return resReturn(user.body())


@require_http_methods(['POST'])
@check_logged_in
def editUser(request, id):
    user = get_object_or_404(XHUser,id=id)
    reqUser = getReqUser(request)
        
    if not reqUser.username == user.username:
        return resError(403)

    data = json.loads(request.body)
    updated = {}
        
    if "username" in data:
        username = data['username']
        if not usernameValidation(username):
            return resError(400, 'Invalid username')
        elif XHUser.objects.filter(username = username).exists():
            return resError(400, 'Username duplicated')
        else:
            user.username = username
            updated = {**updated, 'username_updated': username}

    if "introduction" in data:
        introduction = data['introduction']
        if isString(introduction):
            user.introduction = introduction
            updated = {**updated, 'introduction_updated': introduction}
        else:
            return resError(400, 'invalid introduction')
        
    user.save()
    return resReturn(updated)

@require_http_methods(['DELETE'])
@check_logged_in
def deacUser(request):
    user = get_object_or_404(XHUser,id=id)
    reqUser = getReqUser(request)

    if not reqUser.username == user.username:
        if not reqUser.role == XHUser.RoleChoices.ADMIN:
            return resError(403)

    user.status = XHUser.StatChoices.DEAC
    user.save()

    products = Product.objects.filter(user=user)
    for p in products:
        p.delete()

    return resOk()

@require_http_methods(['DELETE'])
@admin_logged_in
def editStatus(request):
    user = get_object_or_404(XHUser,id=id)

    if user.status == XHUser.StatChoices.DEAC:
        return resError(403, "User is deactivated.")

    if not checkParameter(['status'],request):
        return resMissingPara(['status'])
    
    data = json.loads(request.body)
    status = data['status']

    if not isInt(status) or status not in [XHUser.StatChoices.RESTRT]:
        return resError(400, "Invalid status change")

    user.status = status
    user.save()

    return resOk()

@require_http_methods(['POST'])
@check_logged_in
def editPassword(request):
    user = get_object_or_404(XHUser,id=id)
    reqUser = getReqUser(request)
        
    if reqUser.id != user.id:
        return resError(403 , "User are not allowed to change other user's password.")

    if not checkParameter(['password','newPassword']):
        return resMissingPara(['password','newPassword'])

    data = json.loads(request.body)
    password = data['password']
    newPassword = data['newPassword']

    if not isString(password) or not reqUser.check_password(password):
        return resError(403)

    if not passwordValidation(newPassword):
        return resError(400)

    user.set_password(newPassword)
    login(request, user)
    return resOk()
    

