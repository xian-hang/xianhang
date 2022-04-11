from django.http import HttpResponse

def check_logged_in(view):
    
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view(request, *args, **kwargs)
        else:
            return HttpResponse(status=401)

    return wrap
