from django.db import models
from XHUser.models import XHUser

# Create your models here.
class Report(models.Model):
    class StatChoice(models.IntegerChoices):
        SUB = 0, "Submitted"
        APP = 1, "Approved"
        REJ = 2, "Rejected"

    description = models.CharField(max_length=150)
    status = models.IntegerField(choices=StatChoice.choices, default=0)
    user = models.ForeignKey(XHUser, on_delete=models.SET_NULL, null=True, related_name="creatingReportUser")
    reporting = models.ForeignKey(XHUser, on_delete=models.SET_NULL, null=True, related_name="reportingUser")

    def body(self) -> dict:
        return {
            'id' : self.id,
            'description' : self.description,
            'status' : {self.status : Report.StatChoice(self.status).label},
            'user' : self.user.id,
            'reporting' : self.reporting.id,
        }