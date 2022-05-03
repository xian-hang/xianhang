from django.db import models
from XHUser.models import XHUser

# Create your models here.
class Report(models.Model):
    class StatChoice(models.IntegerChoices):
        PEN = 0, "Pending"
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
            'status' : self.status,
            'userId' : self.user.id if self.user else None,
            'username' : self.user.username if self.user else None,
            'reportingId' : self.reporting.id if self.reporting else None,
            'reportingUsername' : self.reporting.username if self.reporting else None,
        }


class ReportImage(models.Model):
    image = models.FileField(upload_to="reportImage/")
    report = models.ForeignKey(Report, on_delete=models.CASCADE, null=False, blank=False)


class ReportNotice(models.Model):
    content = models.CharField(max_length=150, default=None, null=True)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)

    def body(self) -> dict:
        return {
            'reportId' : self.report.id,
            'content' : self.content,
        }