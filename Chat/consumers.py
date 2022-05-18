
import json

from Chat.models import Message, Chat
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from common.functool import getUser


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

        user = getUser(id = data['userId'])
        reqUser = getReqUser(self.scope)

        chat = getChat(user,reqUser)
        if chat is None:
            chat = Chat.objects.create()
            chat.users.add(user, reqUser)

            async_to_sync(self.channel_layer.group_send)(
                'channel_%s' % user.id,
                {
                    'type' : 'newChat',
                    'chatId' : chat.id,
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
                **message.body(),
            }
        )

    def fetchMessage(self, data):
        userId = data['userId']
        user = getUser(id=userId)
        reqUser = getReqUser(self.scope)
        chat = getChat(user, reqUser)
        if chat is not None:
            messages = Message.objects.filter(chat=chat)
            self.send(text_data=json.dumps({'message' : [m.body() for m in messages]}))

    # command type
    commandTypes = {
        'newMessage' : newMessage,
        'fetchMessage' : fetchMessage,
    }

    def connect(self):
        print('connect : ', self.scope)
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
            # self.send(text_data=json.dumps({'message' : 'connect successfully'}))

    def disconnect(self, test_code):
        print('disconnect : ',self.scope)
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
        print('receive : ', self.scope)
        data = json.loads(text_data)
        self.commandTypes[data['type']](self, data)


    # group command type func
    def newChat(self, data):
        chatId = data['chatId']
        async_to_sync(self.channel_layer.group_add)(
            'chat_%s' % chatId,
            self.channel_name
        )
        messages = Message.objects.filter(chat__id=chatId)
        self.send(text_data=json.dumps({'message' : [m.body() for m in messages]}))


    def sendMessage(self, data):
        message = data['message']
        self.send(text_data=json.dumps(message))
