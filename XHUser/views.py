from itertools import product
import json
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, logout
from Order.models import Order
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404

from xianhang.settings import EMAIL_HOST_USER
from .models import XHUser, Like
from Product.models import Product
from Followership.models import Followership
from common.deco import admin_logged_in, check_logged_in, user_logged_in
from common.functool import checkParameter, clearUser, getActiveUser, getReqUser, getFirstProductImageId
from common.validation import isFloat, isInt, isString, passwordValidation, studentIdValidation, userIdValidation, usernameValidation, keywordValidation
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


@require_http_methods(['OPTIONS', "POST"])
def userLogin(request):
    if not checkParameter(['studentId', 'password'], request):
        return resMissingPara(['studentId', 'password'])

    data = json.loads(request.body)
    studentId = data['studentId']
    password = data['password']

    if not studentIdValidation(studentId) or not isString(password):
        return resUnauthorized("输入格式不正确")

    try:
        user = XHUser.objects.get(studentId=studentId)
    except:
        return resUnauthorized("学号不存在")

    if user.role == XHUser.RoleChoice.ADMIN:
        if user.check_password(data['password']):
            login(request,user)
            token, created = Token.objects.get_or_create(user=user)
            return resReturn({
                'role': user.role,
                'token': token.key,
                'id': user.id
            })
        else:
            return resUnauthorized("密码错误")
    elif user.status in [XHUser.StatChoice.VER, XHUser.StatChoice.RESTRT]:
        if user.check_password(password):
            login(request,user)
            token, created = Token.objects.get_or_create(user=user)
            user.forgotLimit = 5
            user.save()
            return resReturn({
                'role': user.role,
                'token': token.key,
                'id': user.id
            })
        else:
            return resUnauthorized("密码错误")
    elif user.status == XHUser.StatChoice.DEAC:
        return resForbidden("用户已停用账户")
    elif user.status == XHUser.StatChoice.UNVER:
        return resBadRequest("用户还未验证")

    return resUnauthorized("登录失败")


@require_http_methods(['OPTIONS', "POST"])
@check_logged_in
def userLogout(request):
    user = getReqUser(request)
    # Token.objects.filter(user=user).delete()
    logout(request)
    return resOk()


@require_http_methods(['OPTIONS', "POST"])
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
        return resForbidden("学号已被注册")
    
    if XHUser.objects.filter(username=username).exists():
        return resForbidden("用户名已被其他用户使用")

    user = XHUser.objects.create(username=username,
                                 studentId=studentId)
    user.set_password(password)
    user.save()
    # token = Token.objects.create(user=user)

    # sendVerificationMail(user.id)

    return resReturn({'userId' : user.id})


@require_http_methods(['OPTIONS', "POST"])
def resentVerificationEmail(request):
    if not checkParameter(['studentId'], request):
        return resMissingPara(['studentId'])

    data = json.loads(request.body)
    studentId = data['studentId']

    if not studentIdValidation(studentId):
        return resInvalidPara(['studentId'])

    user = get_object_or_404(XHUser, studentId=studentId)
    if user.status != XHUser.StatChoice.UNVER:
        return resBadRequest("该用户已验证")

    if user.verifyLimit <= 0:
        return resForbidden("验证重发次数已用尽，请联络管理员")
    
    user.verifyLimit -= 1
    sendVerificationMail(user.id)
    user.save()
    return resOk()


def verifyEmail(request, key):
    token = get_object_or_404(Token,key=key)
    user = XHUser.objects.get(id=token.user.id)
    if user.status != XHUser.StatChoice.UNVER:
        return resForbidden("用户已验证")
    user.status = XHUser.StatChoice.VER
    user.save()

    token.delete()
    return resOk("Email verified.")


@require_http_methods(['OPTIONS', "POST"])
def forgotPassword(request):
    if not checkParameter(['studentId'],request):
        return resMissingPara(['studentId'])

    data = json.loads(request.body)
    studentId = data['studentId']

    if not (studentIdValidation(studentId) and XHUser.objects.filter(studentId=studentId).exists()):
        return resInvalidPara(['studentId'])

    user = XHUser.objects.get(studentId=studentId)
    if user.status in [XHUser.StatChoice.UNVER, XHUser.StatChoice.DEAC]:
        return resForbidden("该用户并未活跃用户")

    if user.forgotLimit <= 0:
        return resForbidden("无法发送重设密码邮件，请联络管理员")
    
    user.forgotLimit -= 1
    sendResetPasswordMail(user.id)
    user.save()
    
    return resOk("请到 {}@buaa.edu.cn 更换密码".format(studentId))


@require_http_methods(['OPTIONS', "POST"])
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
    user.forgotLimit = 5
    user.save()
    login(request, user)
    token.delete()
    return resOk()


def getUser(request, id):
    user = getActiveUser(id=id)
    if user is None:
        return resNotFound("用户不存在或已注销")

    likeId = None
    followershipId = None
    reqUser = getReqUser(request)
    if reqUser is not None and Like.objects.filter(user=reqUser, liking=user).exists():
        likeId = Like.objects.get(user=reqUser, liking=user).id
    if reqUser is not None and Followership.objects.filter(user=reqUser, following=user).exists():
        followershipId = Followership.objects.get(user=reqUser, following=user).id
    totalLike = Like.objects.filter(liking=user).count()

    return resReturn({**user.body(), 'followershipId': followershipId, 'likeId': likeId, 'totalLike' : totalLike} )


def getUserWithToken(request, key):
    token = get_object_or_404(Token, key=key)
    user = XHUser.objects.get(id=token.user.id)
    return resReturn(user.body())


@check_logged_in
def getProfile(request):
    user = getReqUser(request)
    return getUser(request, user.id)


@require_http_methods(['OPTIONS', 'POST'])
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
            return resBadRequest('用户名已被其他用户使用')
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


@require_http_methods(['OPTIONS', 'DELETE'])
@user_logged_in
def deacUser(request):
    reqUser = getReqUser(request)
    reqUser.status = XHUser.StatChoice.DEAC
    reqUser.save()

    clearUser(reqUser)
    return resOk()


@require_http_methods(['OPTIONS', 'POST'])
@admin_logged_in
def editStatus(request, id):
    user = get_object_or_404(XHUser,id=id)

    if user.status == XHUser.StatChoice.DEAC:
        return resBadRequest("用户并不活跃")

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


@require_http_methods(['OPTIONS', 'POST'])
@admin_logged_in
def editRating(request, id) :
    user = get_object_or_404(XHUser, id=id)

    if not checkParameter(['rating'],request):
        return resMissingPara(['rating'])
    
    data = json.loads(request.body)
    rating = data['rating']

    if isFloat(rating):
        user.rating = rating
        user.save()
        return resOk()
    
    return resBadRequest("Bad Request")


@require_http_methods(['OPTIONS', 'POST'])
@check_logged_in
def editPassword(request):
    reqUser = getReqUser(request)

    if not checkParameter(['password','newPassword'],request):
        return resMissingPara(['password','newPassword'])

    data = json.loads(request.body)
    password = data['password']
    newPassword = data['newPassword']

    if not passwordValidation(newPassword):
        return resBadRequest("密码长度需大于等于 8")

    if not reqUser.check_password(password):
        return resForbidden("原密码不正确")

    reqUser.set_password(newPassword)
    reqUser.save()
    login(request, reqUser)
    return resOk()
    

@require_http_methods(['OPTIONS', 'POST'])
def searchUser(request):
    if not checkParameter(['keyword'], request):
        return resMissingPara(['keyword'])

    data = json.loads(request.body)
    keyword = data['keyword']

    if not keywordValidation(keyword):
        return resInvalidPara(["keyword"])

    users = set(XHUser.objects.filter(username__icontains=keyword, role=XHUser.RoleChoice.USER, status__in=[XHUser.StatChoice.VER, XHUser.StatChoice.RESTRT]))
    users |= set(XHUser.objects.filter(studentId__icontains=keyword, role=XHUser.RoleChoice.USER, status__in=[XHUser.StatChoice.VER, XHUser.StatChoice.RESTRT]))
    if getReqUser(request) is not None:
        users -= {getReqUser(request)}

    return resReturn({"user" : [u.body() for u in users]})


def userProduct(request, id):
    user = get_object_or_404(XHUser, id=id)
    products = set(Product.objects.filter(user=user))
    reqUser = getReqUser(request)
    if reqUser is None or user.id != reqUser.id:
        products -= set(Product.objects.filter(stock=0))
    return resReturn({'result' : [{"product" : p.body(), 'image' : getFirstProductImageId(p)} for p in products]})


@require_http_methods(['OPTIONS', 'POST'])
@user_logged_in
def createLike(request):
    if not checkParameter(['userId'],request):
        return resMissingPara(['userId'])

    data = json.loads(request.body)
    userId = data['userId']
    reqUser = getReqUser(request)
    if userIdValidation(userId) and reqUser.id != userId:
        if not Like.objects.filter(user=reqUser, liking_id=userId).exists():
            like = Like.objects.create(user=reqUser, liking_id=userId)
            return resReturn({'likeId' : like.id})
        else:
            return resBadRequest("Like exists.")
    else:
        return resInvalidPara(['userId'])


@require_http_methods(['OPTIONS', 'DELETE'])
@user_logged_in
def deleteLike(request,id):
    like = get_object_or_404(Like, id=id)
    reqUser = getReqUser(request)

    if like.user.id != reqUser.id:
        return resForbidden("取消赞失败")

    like.delete()
    return resOk()