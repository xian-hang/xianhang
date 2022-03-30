import json
from django.shortcuts import render
from django.core.mail import send_mail
import json

from xianhang.settings import EMAIL_HOST_USER

# Create your views here.
def sendEmailTest(request):
    # data = json.loads(request.body)

    send_mail(
        'Verify your email address for Xian Hang', # subject
        'Thanks for joining us ! Click here for the verification of your email >> NOTHING YET', # message
        EMAIL_HOST_USER, # from email
        ['xianhang2022@gmail.com'], # to email
        fail_silently = False,
    )
