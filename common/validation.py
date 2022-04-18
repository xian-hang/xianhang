def usernameValidation(username) -> bool:
    return isString(username) and len(username) >= 4

def passwordValidation(password) -> bool:
    return isString(password) and len(password) >= 8

def isString(keyword) -> bool:
    return isinstance(keyword, str)

def isInt(keyword) -> bool:
    return isinstance(keyword, int)

def isFloat(keyword) -> bool:
    return isinstance(keyword, float) or isinstance(keyword, int)