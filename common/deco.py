import re
from django.http import HttpResponse
from XHUser.models import XHUser
from rest_framework.authtoken.models import Token

from common.restool import resError
from common.functool import getReqUser

def check_logged_in(view):
    
    def wrap(request, *args, **kwargs):
        user = getReqUser(request)
        if user is None:
            return resError(401)
        else:
            return view(request, *args, **kwargs)

    return wrap


def admin_logged_in(view):

    def wrap(request, *args, **kwargs):
        user = getReqUser(request)
        if user is None:
            return resError(401)
        elif user.role != XHUser.RoleChoices.ADMIN:
            return resError(403, "Only admins are allowed to access this link.")

        return view(request, *args, **kwargs)

    return wrap


def user_logged_in(view):

    def wrap(request, *args, **kwargs):
        user = getReqUser(request)
        if user is None:
            return resError(401)
        elif user.role != XHUser.RoleChoices.USER:
            return resError(403, "Only users are allowed to access this link.")

        return view(request, *args, **kwargs)

    return wrap