import json
from XHUser.models import XHUser
from rest_framework.authtoken.models import Token
from django.core.exceptions import BadRequest

def checkParameter(list, request) -> bool:
    if not request.body:
        # raise BadRequest(str(list) + " is required")
        return False

    data = json.loads(request.body)
    for x in list:
        if not x in data:
            print(x + " is missing")
            # raise BadRequest(str(list) + " is required")
            return False

    return True

def isString(keyword) -> bool:
    return isinstance(keyword, str)

def isInt(keyword) -> bool:
    return isinstance(keyword, int)

def isFloat(keyword) -> bool:
    return isinstance(keyword, float) or isinstance(keyword, int)

def getReqUser(request) -> XHUser:
    if request.user.is_authenticated:
        return XHUser.objects.get(id=request.user.id)
    elif request.META.get('HTTP_AUTHORIZATION') is not None:
        auth = request.META.get('HTTP_AUTHORIZATION').split()
        print(auth)
        if Token.objects.filter(key=auth[1]).exists():
            return Token.objects.filter(key=auth[1])[0].user
    else:
        return None

def usernameValidation(username) -> bool:
    return isString(username) and len(username) >= 4

def passwordValidation(password) -> bool:
    return isString(password) and len(password) >= 8