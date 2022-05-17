
from django.shortcuts import render
from Chat.models import Chat, Message
from django.contrib.auth import login

from common.deco import user_logged_in
from common.functool import getActiveUser, getReqUser, getUser
from common.restool import resNotFound, resOk

# Create your views here.
def messageTime(ele):
    return ele['lastMessage']['time']

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

@user_logged_in
def getChatList(request):
    reqUser = getReqUser(request)
    chats = reqUser.chat_set.all()

    results=[]
    for c in chats:
        messages = Message.objects.filter(chat=c).order_by('-timestamp')
        if len(messages):
            user = c.users.exclude(id=reqUser.id).first()
            results += [{'chatId' : c.id, 'lastMessage' : messages[0].body(), 'username' : user.username}]
    
    results.sort(key=messageTime)
    return resOk({'result' : results})