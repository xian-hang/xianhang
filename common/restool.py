from django.http import JsonResponse, HttpResponse

def resOk(message=""):
    return JsonResponse({'code' : 200, "message" : message})

def resError(code, message=""):
    return JsonResponse({'code' : code, "message" : message}, status=code)

def resMissingPara(list):
    if len(list) == 1:
        return JsonResponse({'code' : 400, "message" : str(list) + " is required."}, status=400)    
    return JsonResponse({'code' : 400, "message" : str(list) + " are required."}, status=400)

def resReturn(data):
    return JsonResponse(data)