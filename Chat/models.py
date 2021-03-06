from django.db import models
from XHUser.models import XHUser
import json

from common.functool import timeToString

# Create your models here.
class Chat(models.Model):
    users = models.ManyToManyField(XHUser)

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE,null=True)
    author = models.ForeignKey(XHUser, on_delete=models.CASCADE)
    message = models.CharField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)
    unread = models.BooleanField(default=True)

    def body(self):
        return {
            'chatId' : self.chat.id,
            'authorId' : self.author.id,
            'author' : self.author.username,
            'message' : self.message,
            'time' : timeToString(self.timestamp),
            'unread' : self.unread,
        }