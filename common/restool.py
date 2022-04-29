from django.http import JsonResponse, HttpResponse, FileResponse

def resOk(message=""):
    return JsonResponse({'code' : 200, "message" : message})

def resError(code, message=""):
    return JsonResponse({'code' : code, "message" : message}, status=code)

def resMissingPara(list):
    if len(list) == 1:
        return JsonResponse({'code' : 400, "message" : str(list) + " is required."}, status=400)    
    return JsonResponse({'code' : 400, "message" : str(list) + " are required."}, status=400)

def resReturn(data):
    return JsonResponse({'code' : 200, **data})

def resInvalidPara(list:str):
    if len(list) == 1:
        return JsonResponse({'code' : 400, "message" : "Invalid " + list[0] + "."}, status=400)   

    s = ""
    for l in list[:-1]:
         s += l + ", "
    s += "or " + list[-1]

    return JsonResponse({'code' : 400, "message" : "Invalid " + s + "."}, status=400)

def resForbidden(message=""):
    return JsonResponse({'code' : 403, "message" : message}, status=403)

def resUnauthorized(message=""):
    return JsonResponse({'code' : 401, "message" : message}, status=401)

def resNotFound(message=""):
    return JsonResponse({'code' : 404, "message" : message}, status=404)

def resBadRequest(message=""):
    return JsonResponse({'code' : 400, "message" : message}, status=400)

def resFile(file):
    return FileResponse(file)

def resImage(image,ext):
    return FileResponse(image, content_type="image/" + ext)
    