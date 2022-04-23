from django.db import models
from XHUser.models import XHUser
# Create your models here.

class Followership(models.Model):
    user = models.ForeignKey(XHUser, null=False, blank=False, on_delete=models.CASCADE, related_name='creatingFollowershipUser')
    following = models.ForeignKey(XHUser, null=False, blank=False, on_delete=models.CASCADE, related_name='followingUser')

    def body(self) -> dict:
        return {
            'id' : self.id,
            'following' : self.following.body(),
        }