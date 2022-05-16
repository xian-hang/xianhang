
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        headers = dict(self.scope['headers'])
        if b'authorization' in headers:
            token = headers[b'authorization'].split()[1]
            
        print('connect : ', self.scope)

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()
        pass

    def disconnect(self, test_code):
        print('disconnect : ',self.scope)
        pass

    def receive(self, text_data=None):
        print('receive : ', self.scope)
        pass