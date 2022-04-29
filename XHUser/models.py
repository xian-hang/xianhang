from ast import mod
import re
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class XHUser(User):

    class StatChoice(models.IntegerChoices):
        UNVER = 0, "Unverified"
        VER = 1, "Verified"
        DEAC = 2, "Deactivated"
        RESTRT = 3, "Restricted"
            
    class RoleChoice(models.IntegerChoices):
        USER = 0, "User"
        ADMIN = 1, "Admin"

    studentId = models.CharField(max_length=150, null=False, blank=False)
    role = models.IntegerField(default=RoleChoice.USER,
                               choices=RoleChoice.choices)
    soldItem = models.IntegerField(default=0)
    rating = models.DecimalField(default=100, decimal_places=1, max_digits=4)
    status = models.IntegerField(default=StatChoice.UNVER,
                                 choices=StatChoice.choices)
    introduction=models.CharField(default="这个人很懒，什么都没留下。", max_length=150)

    def __str__(self) -> str:
        return self.username

    def body(self) -> dict:
        return {
            'id': self.id,
            'username': self.username,
            'studentId': self.studentId,
            'introduction' : self.introduction,
            'role': self.role,
            'soldItem': self.soldItem,
            'rating': self.rating,
            'status': self.status,
        }

class Like(models.Model):
    user = models.ForeignKey(XHUser, null=False, blank=False, related_name="creatingLikeUser", on_delete=models.CASCADE)
    liking = models.ForeignKey(XHUser, null=False, blank=False, related_name="likingUser", on_delete=models.CASCADE)