from Order.models import Order
from Product.models import Product
from XHUser.models import XHUser
from Report.models import Report
from common.functool import getActiveUser


def isString(keyword) -> bool:
    return isinstance(keyword, str)

def isInt(keyword) -> bool:
    return isinstance(keyword, int)

def isFloat(keyword) -> bool:
    return isinstance(keyword, float) or isinstance(keyword, int)


# XHUser validation
def usernameValidation(username) -> bool:
    return isString(username) and len(username) >= 4

def passwordValidation(password) -> bool:
    return isString(password) and len(password) >= 8

def userIdValidation(id) -> bool:
    return isInt(id) and XHUser.objects.filter(id=id).exists() and getActiveUser(id=id) is not None

def studentIdValidation(id) -> bool:
    return isString(id) and len(id) >= 1


# Product validation
def stockValidation(stock) -> bool:
    return isInt(stock) and stock >= 0

def priceValidation(price) -> bool:
    return isFloat(price) and price >= 0

def keywordValidation(keyword) -> bool:
    return isString(keyword) and len(keyword) >= 1

def pickUpLocValidation(pickUpLoc) -> bool:
    return isString(pickUpLoc) and len(pickUpLoc) >= 1

def tradingMethodValidation(method) -> bool:
    return isInt(method) and method in Product.TradingMethod._value2member_map_

def productIdValidation(id) -> bool:
    return isInt(id) and Product.objects.filter(id=id).exists()

def nameValidation(name) -> bool:
    return isString(name) and len(name) >= 1

def descriptionValidation(description) -> bool:
    return isString(description) and len(description) >= 1


# Order validation
# nameValidation same as Product's
def priceValidation(price) -> bool:
    return isFloat(price) and price >= 0

def postageValidation(postage) -> bool:
    return isFloat(postage) and postage >= 0

def amountValidation(amount) -> bool:
    return isInt(amount) and amount >= 1

def phoneNumValidation(phoneNum) -> bool:
    return isString(phoneNum) and len(phoneNum) == 11 and phoneNum.isdigit()

def deliveringAddrValidation(deliveringAddr) -> bool:
    return isString(deliveringAddr) and len(deliveringAddr) >= 1

def orderStatusValidation(status) -> bool:
    return isInt(status) and status in Order.StatChoice._value2member_map_

def pickedTradingMethodValidation(method) -> bool:
    return isInt(method) and method in Order.TradingMethod._value2member_map_


# Report validation
# descriptionValidation same as Product's
def reportingIdValidation(id) -> bool:
    return userIdValidation(id)

def reportStatusValidation(status) -> bool:
    return isInt(status) and status in Report.StatChoice._value2member_map_
