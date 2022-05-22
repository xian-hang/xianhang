
import json

from Chat.models import Message, Chat
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from common.functool import getActiveUser, getUser


def getToken(scope):
    headers = dict(scope['headers'])
    if b'authorization' in headers:
        return headers[b'authorization'].split()[1].decode('ascii')

def getReqUser(scope):
    token = getToken(scope)
    if token is not None:
        return getUser(token=token)
    if scope['user'].is_authenticated:
        print(scope['user'].id)
        return getUser(id=scope['user'].id)

def getChat(user1,user2):
    chat = set(user1.chat_set.all()) & set(user2.chat_set.all())
    if len(chat):
        return chat.pop()

class ChatConsumer(WebsocketConsumer):

    #command func
    def newMessage(self, data):

        user = getActiveUser(id = data['userId'])
        if user is None:
            print("WS ERROR : Invalid user.")
            return
        reqUser = getReqUser(self.scope)
        if reqUser is None:
            print("WS ERROR : User havent logged in.")
            return

        chat = getChat(user,reqUser)
        if chat is None:
            chat = Chat.objects.create()
            chat.users.add(user, reqUser)

            async_to_sync(self.channel_layer.group_send)(
                'channel_%s' % user.id,
                {
                    'type' : 'newChat',
                    'chatId' : chat.id,
                    'userId' : user.id,
                    'message' : 'add new chat'
                }
            )

            async_to_sync(self.channel_layer.group_add)(
                'chat_%s' % chat.id,
                self.channel_name
            )
        
        message = Message.objects.create(message=data['message'], author= reqUser,chat=chat)
        async_to_sync(self.channel_layer.group_send)(
            'chat_%s' % chat.id,
            {
                'type' : 'sendMessage',
                'message' : message.body(),
            }
        )

    def readMessage(self, data):
        userId = data['userId']
        user = getUser(id=userId)
        if user is None:
            print('WS ERROR : User not found.')
            return
        reqUser = getReqUser(self.scope)
        if reqUser is None:
            print('WS ERROR : User havent logged in.')
            return

        chat = getChat(user, reqUser)
        if chat is not None:
            unread = Message.objects.filter(chat=chat, unread=True).exclude(author=reqUser)
            for m in unread:
                m.unread = False
                m.save()

    # command type
    commandTypes = {
        'newMessage' : newMessage,
        'readMessage' : readMessage,
    }

    def connect(self):
        # print('connect : ', self.scope)
        reqUser = getReqUser(self.scope)
        if reqUser is not None:
            async_to_sync(self.channel_layer.group_add)(
                'channel_%s' % reqUser.id,
                self.channel_name
            )

            chats = reqUser.chat_set.all()
            for c in chats:
                async_to_sync(self.channel_layer.group_add)(
                    'chat_%s' % c.id,
                    self.channel_name
                )

            self.accept()
            self.send(text_data='0' + json.dumps({'result' : [{'chatId' : c.id, 
                                                                'message' : [m.body() for m in Message.objects.filter(chat=c)], 
                                                                'username' : c.users.exclude(id=reqUser.id).first().username, 
                                                                'userId' : c.users.exclude(id=reqUser.id).first().id,
                                                                'unread' : len(Message.objects.filter(chat=c, unread=True).exclude(author=reqUser)),
                                                                } for c in chats ]}))
            # self.send(text_data=json.dumps({'message' : 'connect successfully'}))
        else :
            print('WS ERROR : User havent logged in.')

    def disconnect(self, test_code):
        # print('disconnect : ',self.scope)
        # self.send(text_data=json.dumps({'message' : 'disconnect successfully'}))

        reqUser = getReqUser(self.scope)
        if reqUser is not None:

            async_to_sync(self.channel_layer.group_discard)(
                'channel_%s' % reqUser.id,
                self.channel_name
            )

            chats = reqUser.chat_set.all()
            for c in chats:
                async_to_sync(self.channel_layer.group_discard)(
                    'chat_%s' % c.id,
                    self.channel_name
                )

    def receive(self, text_data=None):
        # print('receive : ', self.scope)
        data = json.loads(text_data)
        self.commandTypes[data['type']](self, data)


    # group command type func
    def newChat(self, data):
        chatId = data['chatId']
        userId = data['userId']
        async_to_sync(self.channel_layer.group_add)(
            'chat_%s' % chatId,
            self.channel_name
        )
        
        chat = Chat.objects.get(id=chatId)
        user = getActiveUser(id=userId)
        self.send(text_data='2' + json.dumps({'chatId' : chat.id, 
                                                'message' : [m.body() for m in Message.objects.filter(chat=chat)], 
                                                'username' : chat.users.exclude(id=user.id).first().username, 
                                                'userId' : chat.users.exclude(id=user.id).first().id,
                                                'unread' : len(Message.objects.filter(chat=chat, unread=True).exclude(author=user)),
                                                } ))


    def sendMessage(self, data):
        message = data['message']
        self.send(text_data='1' + json.dumps(message))
