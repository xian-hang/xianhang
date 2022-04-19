from django.core.mail import send_mail
from xianhang.settings import EMAIL_HOST_USER, BASE_URL
from django.core.exceptions import BadRequest

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

def sendVerificationMail(userId,studentId,username):
    try:
        send_mail(
            '[Xian Hang] Verify your emil address',  # subject
            'Hi, %s! \n\n Thanks for joining us ! Click here to confirm your email >> %suser/%s/verify/' % (username, BASE_URL, userId),  # message
            EMAIL_HOST_USER,  # from email
            [studentId + '@buaa.edu.cn'],  # to email
        )
    except Exception as e:
        print(e)
        raise BadRequest(message="Send mail failed")