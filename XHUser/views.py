import json
import re
from smtplib import SMTPAuthenticationError
from wsgiref import headers
from django.shortcuts import render
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods

from xianhang.settings import EMAIL_HOST_USER
from .models import XHUser
from xianhang.deco import check_logged_in
from xianhang.functool import checkParameter


# Create your views here.
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
def login(request):
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
            login(user)
            return JsonResponse({
                'detail': 'logged in succesfully',
                'role': 'admin'
            })
    elif user.status == XHUser.StatChoices.VER | user.status == XHUser.StatChoices.REST:
        if user.check_password(password):
            login(user)
            return JsonResponse({
                'detail': 'logged in succesfully',
                'role': 'user'
            })

    return HttpResponse(status=401)


@require_http_methods(["POST"])
@check_logged_in
def logout(request):
    logout()
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
                                 password=password,
                                 studentId=studentId)
    send_mail(
        'Verify your email address for Xian Hang',  # subject
        'Thanks for joining us ! Click here for the verification of your email >> http://localhost:8000/user/%s/verify/' % user.id,  # message
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


@require_http_methods(["GET","POST","DELETE"])
def user(request, id):
    try:
        user = XHUser.objects.get(id=id)
    except XHUser.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        return JsonResponse(user.body())
    else :
        return JsonResponse({'detail' : 'method coming soon'})
