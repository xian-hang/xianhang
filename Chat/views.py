from email import message
from django.shortcuts import render
from Chat.models import Chat
from django.contrib.auth import login

from common.deco import user_logged_in
from common.functool import getActiveUser, getReqUser, getUser
from common.restool import resNotFound, resOk

# Create your views here.

def loginTest(request):
    user=getUser(id=7)
    print(user)
    login(request, user)
    return resOk()

def index(request):
    return render(request, 'chat/index.html', {})

def room(request, userId):
    return render(request, 'chat/room.html', {
        'userId': userId
    })

@user_logged_in
def getChat(request, userId):
    user = getActiveUser(id=userId)
    if user is None:
        return resNotFound("User not found.")

    reqUser = getReqUser(request)
    chat = set(user.chat_set.all()) & set(reqUser.chat_set.all())

    if len(chat) == 0:
        chat = Chat.objects.create()
        chat.users.add(reqUser,user)
    else:
        chat = chat.pop()

    messages = chat.messages_set.all()

    return resOk({'id' : chat.id, 'username' : user.username, 'messages' : [m.body() for m in messages]})

