import json
from django.core.mail import send_mail
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, logout
from Product.views import product
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404

from xianhang.settings import EMAIL_HOST_USER, BASE_URL
from .models import XHUser
from Product.models import Product
from common.deco import check_logged_in
from common.functool import checkParameter, getActiveUser, getReqUser, getObjectOrResError
from common.validation import isString, passwordValidation, usernameValidation 
from common.restool import resError, resMissingPara, resOk, resReturn

# Create your views here.
def checkReq(request):
    print(getActiveUser(id=17))
    # print(request.META)
    return resOk()


def sendEmailTest(request):
    # data = json.loads(request.body)
    try:
        send_mail(
            '[Testing] Verify your email address for Xian Hang',  # subject
            'Thanks for joining us !',  # message
            EMAIL_HOST_USER,  # from email
            ['xianhang2022@gmail.com'],  # to email
        )
    except Exception as e:
        print(e)
        return resError(403, 'An error occured')

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
        user = XHUser.objects.get_ob(studentId=studentId)
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

    if not usernameValidation(username) or not passwordValidation(password):
        return resError(400, "Invalid username or password.")

    if XHUser.objects.filter(studentId=studentId).exists() or XHUser.objects.filter(username=username).exists():
        return resError(403)

    user = XHUser.objects.create(username=username,
                                 studentId=studentId)
    user.set_password(password)
    user.save()
    # token = Token.objects.create(user=user)

    send_mail(
        '[Xian Hang] Verify your emil address',  # subject
        'Hi, %s! \n\n Thanks for joining us ! Click here to confirm your email >> %suser/%s/verify/' % (user.username, BASE_URL, user.id),  # message
        EMAIL_HOST_USER,  # from email
        [studentId + '@buaa.edu.cn'],  # to email
    )
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
    

