from django.core.mail import send_mail
from XHUser.models import XHUser
from xianhang.settings import EMAIL_HOST_USER, BASE_URL
from django.core.exceptions import BadRequest
from rest_framework.authtoken.models import Token

def mailtest():
    try:
        send_mail(
            '[Testing] Verify your email address for Xian Hang',  # subject
            'Thanks for joining us !',  # message
            EMAIL_HOST_USER,  # from email
            ['xianhang2022@gmail.com'],  # to email
        )
    except Exception as e:
        print(e)
        raise BadRequest


def sendVerificationMail(userId):
    try:
        user = XHUser.objects.get(id=userId)
        if Token.objects.filter(user=user).exists():
            Token.objects.get(user=user).delete()
        
        token = Token.objects.create(user=user)

        send_mail(
            '[Xian Hang] Verify your emil address',  # subject
            'Hi, %s! \n\n Thanks for joining us ! Click here to confirm your email >> %suser/%s/verify/' % (user.username, BASE_URL, token.key),  # message
            EMAIL_HOST_USER,  # from email
            [user.studentId + '@buaa.edu.cn'],  # to email
        )
    except Exception as e:
        print(e)
        raise BadRequest(message="Send mail failed")