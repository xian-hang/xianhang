import json
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, logout
from Order.models import Order
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404

from xianhang.settings import EMAIL_HOST_USER
from .models import XHUser, Like
from Product.models import Product
from common.deco import admin_logged_in, check_logged_in, user_logged_in
from common.functool import checkParameter, clearUser, getActiveUser, getReqUser
from common.validation import isInt, isString, passwordValidation, studentIdValidation, userIdValidation, usernameValidation, keywordValidation
from common.restool import resBadRequest, resForbidden, resInvalidPara, resMissingPara, resNotFound, resOk, resReturn, resUnauthorized
from common.mail import mailtest, sendResetPasswordMail, sendVerificationMail

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

    if not studentIdValidation(studentId) or not isString(password):
        return resUnauthorized()

    try:
        user = XHUser.objects.get(studentId=studentId)
    except:
        return resUnauthorized()

    if user.role == XHUser.RoleChoice.ADMIN:
        if user.check_password(data['password']):
            login(request,user)
            token, created = Token.objects.get_or_create(user=user)
            return resReturn({
                'role': user.role,
                'token': token.key,
                'id': user.id
            })
    elif user.status in [XHUser.StatChoice.VER, XHUser.StatChoice.RESTRT]:
        if user.check_password(password):
            login(request,user)
            token, created = Token.objects.get_or_create(user=user)
            return resReturn({
                'role': user.role,
                'token': token.key,
                'id': user.id
            })
    elif user.status == XHUser.StatChoice.DEAC:
        return resForbidden()
    elif user.status == XHUser.StatChoice.UNVER:
        return resBadRequest()

    return resUnauthorized()


@require_http_methods(["POST"])
@check_logged_in
def userLogout(request):
    user = getReqUser(request)
    # Token.objects.filter(user=user).delete()
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

    if not (usernameValidation(username) and passwordValidation(password) and studentIdValidation(studentId)):
        return resInvalidPara(["username", "studentId", "password"])

    if XHUser.objects.filter(studentId=studentId).exists():
        return resForbidden("Given student id exists.")
    
    if XHUser.objects.filter(username=username).exists():
        return resForbidden("Given username exists.")

    user = XHUser.objects.create(username=username,
                                 studentId=studentId)
    user.set_password(password)
    user.save()
    # token = Token.objects.create(user=user)

    sendVerificationMail(user.id)

    return resReturn({'userId' : user.id})


@require_http_methods(["POST"])
def resentVerificationEmail(request, id):
    user = get_object_or_404(XHUser, id=id)
    if user.status != XHUser.StatChoice.UNVER:
        return resBadRequest("User's email is verified.")
    
    sendVerificationMail(user.id)
    return resOk()


def verifyEmail(request, key):
    token = get_object_or_404(Token,key=key)
    user = XHUser.objects.get(id=token.user.id)
    if user.status != XHUser.StatChoice.UNVER:
        return resForbidden()
    user.status = XHUser.StatChoice.VER
    user.save()

    token.delete()
    return resOk("Email verified.")


@require_http_methods(["POST"])
def forgotPassword(request):
    if not checkParameter(['studentId'],request):
        return resMissingPara(['studentId'])

    data = json.loads(request.body)
    studentId = data['studentId']

    if not (studentIdValidation(studentId) and XHUser.objects.filter(studentId=studentId).exists()):
        return resInvalidPara(['studentId'])

    user = XHUser.objects.get(studentId=studentId)
    if user.status in [XHUser.StatChoice.UNVER, XHUser.StatChoice.DEAC]:
        return resForbidden("User's account is not active.")
    
    sendResetPasswordMail(user.id)
    
    return resOk("Email sent.")


@require_http_methods(["POST"])
def resetPassword(request,key):
    token = get_object_or_404(Token,key=key)
    user = XHUser.objects.get(id=token.user.id)

    if not checkParameter(['newPassword'],request):
        return resMissingPara(['newPassword'])

    data = json.loads(request.body)
    newPassword = data['newPassword']

    if not passwordValidation(newPassword):
        return resInvalidPara(['newPassword'])
    
    user.set_password(newPassword)
    login(request, user)
    token.delete()
    return resOk()


def getUser(request, id):
    user = getActiveUser(id=id)
    if user is None:
        return resNotFound()

    likeId = None
    reqUser = getReqUser(request)
    if reqUser is not None and Like.objects.filter(user=reqUser, liking=user).exists():
        likeId = Like.objects.get(user=reqUser, liking=user).id
    totalLike = Like.objects.filter(liking=user).count()

    return resReturn({**user.body(), 'likeId': likeId, 'totalLike' : totalLike} )


@check_logged_in
def getProfile(request):
    user = getReqUser(request)
    return getUser(request, user.id)


@require_http_methods(['POST'])
@check_logged_in
def editUser(request):
    reqUser = getReqUser(request)

    if not request.body:
        return resBadRequest("Empty parameter.")

    data = json.loads(request.body)
    # updated = {}
        
    if "username" in data:
        username = data['username']
        if not usernameValidation(username):
            return resInvalidPara(["username"])
        elif username != reqUser.username and XHUser.objects.filter(username = username).exists():
            return resBadRequest('Username duplicated')
        else:
            reqUser.username = username
            # updated = {**updated, 'username_updated': username}

    if "introduction" in data:
        introduction = data['introduction']
        if isString(introduction):
            reqUser.introduction = introduction
            # updated = {**updated, 'introduction_updated': introduction}
        else:
            return resInvalidPara(["introduction"])
        
    reqUser.save()
    return resOk()


@require_http_methods(['DELETE'])
@user_logged_in
def deacUser(request):
    reqUser = getReqUser(request)
    reqUser.status = XHUser.StatChoice.DEAC
    reqUser.save()

    clearUser(reqUser)
    return resOk()


@require_http_methods(['DELETE'])
@admin_logged_in
def editStatus(request, id):
    user = get_object_or_404(XHUser,id=id)

    if user.status == XHUser.StatChoice.DEAC:
        return resBadRequest("User is deactivated.")

    if not checkParameter(['status'],request):
        return resMissingPara(['status'])
    
    data = json.loads(request.body)
    status = data['status']

    if status == XHUser.StatChoice.RESTRT:
        user.status = status
        user.save()

        products = Product.objects.filter(user=user)
        for p in products:
            p.stock = 0
            p.save()

        return resOk()

    elif status == XHUser.StatChoice.DEAC:
        user.status = status
        user.save()
        clearUser(user)
        return resOk()
    
    else:
        return resInvalidPara(['status'])

@require_http_methods(['POST'])
@check_logged_in
def editPassword(request):
    reqUser = getReqUser(request)

    if not checkParameter(['password','newPassword'],request):
        return resMissingPara(['password','newPassword'])

    data = json.loads(request.body)
    password = data['password']
    newPassword = data['newPassword']

    if not isString(password) or not reqUser.check_password(password):
        return resForbidden()

    if not passwordValidation(newPassword):
        return resBadRequest()

    reqUser.set_password(newPassword)
    reqUser.save()
    login(request, reqUser)
    return resOk()
    

@require_http_methods(['POST'])
def searchUser(request):
    if not checkParameter(['keyword'], request):
        return resMissingPara(['keyword'])

    data = json.loads(request.body)
    keyword = data['keyword']

    if not keywordValidation(keyword):
        return resInvalidPara(["keyword"])

    users = set(XHUser.objects.filter(username__contains=keyword))
    users |= set(XHUser.objects.filter(studentId__contains=keyword))

    return resReturn({"user" : [u.body() for u in users]})


def userProduct(request, id):
    products = Product.objects.filter(user=id)
    return resReturn({"product" : [p.body() for p in products]})


@require_http_methods(['POST'])
@user_logged_in
def createLike(request):
    if not checkParameter(['userId'],request):
        return resMissingPara(['userId'])

    data = json.loads(request.body)
    userId = data['userId']
    reqUser = getReqUser(request)
    if userIdValidation(userId) and reqUser.id != userId:
        if not Like.objects.filter(user=reqUser, liking_id=userId).exists():
            Like.objects.create(user=reqUser, liking_id=userId)
            return resOk()
        else:
            return resBadRequest("Like exists.")
    else:
        return resInvalidPara(['userId'])


@require_http_methods(['DELETE'])
@user_logged_in
def deleteLike(request,id):
    like = get_object_or_404(Like, id=id)
    reqUser = getReqUser(request)

    if like.user.id != reqUser.id:
        return resForbidden()

    like.delete()
    return resOk()