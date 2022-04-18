from django.http import JsonResponse, HttpResponse

def resOk(message=""):
    return HttpResponse({'code' : 200, "message" : message})

def resError(code, message=""):
    return JsonResponse({'code' : 200, "message" : message}, status=code)

def resMissingPara(list):
    return JsonResponse({'code' : 400, "message" : str(list) + " is required."}, status=400)

def resReturn(data):
    return JsonResponse(data)