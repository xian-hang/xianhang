from Product.models import Product

def usernameValidation(username) -> bool:
    return isString(username) and len(username) >= 4

def passwordValidation(password) -> bool:
    return isString(password) and len(password) >= 8

def stockValidation(stock) -> bool:
    return isInt(stock) and stock >= 0

def priceValidation(price) -> bool:
    return isFloat(price) and price >= 0

def keywordValidation(keyword) -> bool:
    return isString(keyword) and len(keyword) >= 1

def pickUpLocValidation(pickUpLoc) -> bool:
    return isString(pickUpLoc) and len(pickUpLoc) >= 1

def tradingMethodValidation(tradingMethod) -> bool:
    return isInt(tradingMethod) and tradingMethod in Product.TradingMethod._value2member_map_

def isString(keyword) -> bool:
    return isinstance(keyword, str)

def isInt(keyword) -> bool:
    return isinstance(keyword, int)

def isFloat(keyword) -> bool:
    return isinstance(keyword, float) or isinstance(keyword, int)