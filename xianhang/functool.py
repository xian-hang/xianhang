import json


def checkParameter(list, request):
    if not request.body:
        return False

    data = json.loads(request.body)
    for x in list:
        print(x)
        if not x in data:
            print(x + "is missing")
            return False

    return True

def isString(string):
    return isinstance(string, str)