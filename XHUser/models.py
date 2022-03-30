from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class XHUser(User):
    STAT_CHOICE= (
        (0, "Unverified"),
        (1, "Verified"),
        (2, "Deactivated"),
        (3, "Restricted"),
    )

    studentId = models.IntegerField()
    soldItem = models.IntegerField(default=0)
    rating = models.DecimalField(default=100, decimal_places=1, max_digits=4)
    status = models.IntegerField(default=0, choices=STAT_CHOICE)

    def __str__(self):
        return self.username