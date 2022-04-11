import re
from django.http import HttpResponse
from XHUser.models import XHUser

def check_logged_in(view):
    
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view(request, *args, **kwargs)
        else:
            return HttpResponse(status=401)

    return wrap


def admin_logged_in(view):

    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            user = XHUser.objects.get(username=request.user.username)
            if user.role == XHUser.RoleChoices.ADMIN:
                return view(request, *args, **kwargs)
            else:
                return HttpResponse(status=403)
        else:
            return HttpResponse(status=401)

    return wrap

def user_logged_in(view):

    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            user = XHUser.objects.get(username=request.user.username)
            if user.role == XHUser.RoleChoices.USER:
                return view(request, *args, **kwargs)
            else:
                return HttpResponse(status=403)
        else:
            return HttpResponse(status=401)

    return wrap