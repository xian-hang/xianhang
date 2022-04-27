from itertools import islice
import json
from logging import raiseExceptions
from XHUser.models import XHUser
from Product.models import Product
from Order.models import Order
from rest_framework.authtoken.models import Token
from django.core.exceptions import BadRequest, PermissionDenied, ObjectDoesNotExist


from django.db.models.base import Model
from typing import Type, TypeVar
from common.restool import resError
from django.http import Http404
from django.utils import timezone

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

def getReqUser(request) -> XHUser:
    if request.user.is_authenticated:
        return XHUser.objects.get(id=request.user.id)
    elif request.META.get('HTTP_AUTHORIZATION') is not None:
        auth = request.META.get('HTTP_AUTHORIZATION').split()
        if Token.objects.filter(key=auth[1]).exists():
            token = Token.objects.get(key=auth[1])
            user = XHUser.objects.get(id=token.user.id)
            return user
    else:
        return None

def getActiveUser(*args, **kwargs) -> XHUser:
    try:
        user = XHUser.objects.get(*args, **kwargs)
        if user.role == XHUser.RoleChoice.USER and user.status in [XHUser.StatChoice.VER, XHUser.StatChoice.RESTRT]:
            return user
    except:
        pass
    
    return None

def pickUpAvailable(method) -> bool:
    return method in [Product.TradingMethod.PICKUP, Product.TradingMethod.BOTH]

_T = TypeVar("_T", bound=Model)
def getObjectOrResError(errCode = 0, returnNone = False, klass: Type[_T] = None, *args, **kwargs) -> _T : 
    if klass is None:
        raise Http404

    key = dict(islice(kwargs.items(),0,1))
    try:
        obj = klass.objects.get(**key)
    except Exception as e:
        if errCode == 404:
            raise Http404
        elif errCode == 403:
            raise PermissionDenied
        elif errCode == 400:
            raise BadRequest
        elif returnNone:
            return None
        else:
            raise e
    
    return obj

def saveFormOr400(form):
    if form.is_valid():
        try:
            return form.save(commit=False)
        except Exception as e:
            raise BadRequest(e)
    else:
        raise BadRequest

def clearUser(user):
    products = Product.objects.filter(user=user)
    for p in products:
        p.delete()

    orders = Order.objects.filter(user=user, status=Order.StatChoice.UNPAID)
    for o in orders:
        o.status = Order.StatChoice.CANC
        o.save()
    