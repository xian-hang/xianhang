import json


def checkParameter(list, request):
    if not request.body:
        return False

    data = json.loads(request.body)
    for x in list:
        if not x in data:
            print(x + " is missing")
            return False

    return True

def isString(keyword):
    return isinstance(keyword, str)

def isInt(keyword):
    return isinstance(keyword, int)

def isFloat(keyword):
    return isinstance(keyword, float) or isinstance(keyword, int)