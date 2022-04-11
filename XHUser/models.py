from ast import mod
import re
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class XHUser(User):

    class StatChoices(models.IntegerChoices):
        UNVER = 0, "Unverified"
        VER = 1, "Verified"
        DEAC = 2, "Deactivated"
        RESTRT = 3, "Restricted"
            


    class RoleChoices(models.IntegerChoices):
        USER = 0, "User"
        ADMIN = 1, "Admin"

    studentId = models.CharField(max_length=150, null=False, blank=False)
    role = models.IntegerField(default=RoleChoices.USER,
                               choices=RoleChoices.choices)
    soldItem = models.IntegerField(default=0)
    rating = models.DecimalField(default=100, decimal_places=1, max_digits=4)
    status = models.IntegerField(default=StatChoices.UNVER,
                                 choices=StatChoices.choices)

    def __str__(self) -> str:
        return self.username

    def body(self) -> dict:
        return {
            'username': self.username,
            'studentId': self.studentId,
            'role': XHUser.RoleChoices(self.role).label,
            'soldItem': self.soldItem,
            'rating': self.rating,
            'status': XHUser.StatChoices(self.status).label,
        }