import json
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, logout
from Product.views import product

from xianhang.settings import EMAIL_HOST_USER
from .models import XHUser
from Product.models import Product
from xianhang.deco import check_logged_in
from xianhang.functool import checkParameter, isString


# Create your views here.
def checkReq(request):
    print(request.META)
    return HttpResponse()


def sendEmailTest(request):
    # data = json.loads(request.body)

    try:
        send_mail(
            'Verify your email address for Xian Hang',  # subject
            'Thanks for joining us ! Click here for the verification of your email >> NOTHING YET',  # message
            EMAIL_HOST_USER,  # from email
            ['xianhang2022@gmail.com'],  # to email
        )
    except Exception as e:
        print(e)
        return JsonResponse({'detail': 'An error occured'}, status=400)

    return JsonResponse({'detail': 'Sent successfully'})


@require_http_methods(["POST"])
def userLogin(request):
    try:
        data = json.loads(request.body)
        studentId = data['studentId']
        password = data['password']
    except:
        return HttpResponse(status=401)

    try:
        user = XHUser.objects.get(studentId=studentId)
    except XHUser.DoesNotExist:
        return HttpResponse(status=401)

    if user.role == XHUser.RoleChoices.ADMIN:
        if user.check_password(data['password']):
            login(request,user)
            return JsonResponse({
                'detail': 'logged in succesfully',
                'role': 'admin'
            })
    elif user.status == XHUser.StatChoices.VER or user.status == XHUser.StatChoices.RESTRT:
        if user.check_password(password):
            login(request,user)
            return JsonResponse({
                'detail': 'logged in succesfully',
                'role': 'user'
            })

    return HttpResponse(status=401)


@require_http_methods(["POST"])
@check_logged_in
def userLogout(request):
    logout(request)
    return JsonResponse({'detail': 'logged out successfully'})


@require_http_methods(["POST"])
def createUser(request):
    if not checkParameter(['username', 'studentId', 'password'], request):
        return HttpResponse(status=400)

    data = json.loads(request.body)
    username = data['username']
    studentId = data['studentId']
    password = data['password']

    if len(username) < 4 | len(password) < 8:
        return HttpResponse(status=400)

    users = []
    users += XHUser.objects.filter(studentId=studentId)
    users += XHUser.objects.filter(username=username)
    if len(users):
        return HttpResponse(status=403)

    user = XHUser.objects.create(username=username,
                                 studentId=studentId)
    user.set_password(password)
    user.save()

    send_mail(
        '[Xian Hang] Verify your emil address',  # subject
        'Hi, %s! \n\n Thanks for joining us ! Click here to confirm your email >> http://localhost:8000/user/%s/verify/' % (user.username, user.id),  # message
        EMAIL_HOST_USER,  # from email
        [studentId + '@buaa.edu.cn'],  # to email
    )
    return JsonResponse({'detail': 'email sent'})


def verifyEmail(request, id):
    try:
        user = XHUser.objects.get(id=id)
        if not user.status == XHUser.StatChoices.UNVER:
            return HttpResponse(status=403)
        user.status = XHUser.StatChoices.VER
        user.save()
        return JsonResponse({'detail': 'email verified'})
    except:
        return HttpResponse(status=404)


def user(request, id):
    try:
        user = XHUser.objects.get(id=id)
    except XHUser.DoesNotExist:
        return HttpResponse(status=404)

    return JsonResponse(user.body())


@require_http_methods(['POST','DELETE'])
@check_logged_in
def editUser(request):
    try:
        user = XHUser.objects.get(id=id)
    except XHUser.DoesNotExist:
        return HttpResponse(status=404)
        
    if request.method == 'POST':
        if not request.user.username == user.username:
            return HttpResponse(status = 403)

        data = json.loads(request.body)
        changed = []
        
        if "password" in data:
            password = data['password']
            if isString(password) and len(password) >= 8:
                user.set_password(password)
                changed += ['password']
            else:
                return JsonResponse({'detail' : 'invalid password'}, status=400)
        
        user.save()
        return JsonResponse({'changed' : changed})

    elif request.method == 'DELETE':
        if not request.user.username == user.username:
            reqUser = XHUser.objects.get(username = request.user)
            if not reqUser.role == XHUser.RoleChoices.ADMIN:
                return HttpResponse(status = 403)

        user.status = XHUser.StatChoices.DEAC
        user.save()

        products = Product.objects.filter(user=user)
        for p in products:
            p.delete()

        return HttpResponse()


