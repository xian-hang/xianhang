import re
from django.http import HttpResponse
from XHUser.models import XHUser
from rest_framework.authtoken.models import Token
from common.restool import resError

def check_logged_in(view):
    
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view(request, *args, **kwargs)
        elif request.META.get('HTTP_AUTHORIZATION') is not None:
            auth = request.META.get('HTTP_AUTHORIZATION').split()
            print(auth)
            if Token.objects.filter(key=auth[1]).exists():
                return view(request, *args, **kwargs)
            else:
                return resError(401)
        else:
            return resError(401)

    return wrap


def admin_logged_in(view):

    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            user = XHUser.objects.get(username=request.user.username)
            if user.role == XHUser.RoleChoices.ADMIN:
                return view(request, *args, **kwargs)
            else:
                return resError(403, "Only admins are allowed to access this link.")
        else:
            return resError(401)

    return wrap

def user_logged_in(view):

    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            user = XHUser.objects.get(username=request.user.username)
            if user.role == XHUser.RoleChoices.USER:
                return view(request, *args, **kwargs)
            else:
                return resError(403, "Only users are allowed to access this link.")
        else:
            return resError(401)

    return wrap