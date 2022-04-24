import json
from django.shortcuts import render, get_object_or_404
from Report.models import Report
from django.views.decorators.http import require_http_methods

from common.deco import admin_logged_in, user_logged_in
from common.functool import checkParameter, getActiveUser, getReqUser
from common.restool import resBadRequest, resForbidden, resInvalidPara, resMissingPara, resOk, resReturn
from common.validation import descriptionValidation, reportStatusValidation, reportingIdValidation

# Create your views here.
@require_http_methods(['POST'])
@user_logged_in
def createReport(request):
    if not checkParameter(['description', 'reportingId'], request):
        return resMissingPara(['description', 'reportingId'])

    data = json.loads(request.body)
    description = data['description']
    reportingId = data['reportingId']

    if not (descriptionValidation(description) and reportingIdValidation(reportingId)):
        return resInvalidPara(['description', 'reportingId'])

    reporting = getActiveUser(id=reportingId)
    reqUser = getReqUser(request)
    if reqUser.id == reportingId:
        return resForbidden("Users are not allowed to report themselves.")

    if Report.objects.filter(user=reqUser, reporting=reporting, status=Report.StatChoice.SUB):
        return resForbidden("User has submitted a same report which has not been reviewed yet.")

    Report.objects.create(user=reqUser, description=description, reporting=reporting)
    return resOk()


@admin_logged_in
def getReport(request, id):
    report = get_object_or_404(Report, id=id)
    return resReturn(report.body())


@require_http_methods(['POST'])
@admin_logged_in
def editReport(request, id):
    report = get_object_or_404(Report, id=id)

    if not checkParameter(['status'], request):
        return resMissingPara(['status'])

    data = json.loads(request.body)
    status = data['status']

    if not reportStatusValidation(status):
        return resInvalidPara(['status'])
    
    if report.status != Report.StatChoice.SUB:
        return resBadRequest("Report status is not allowed to be changed anymore.")

    report.status = status
    report.save()
    return resOk()


@require_http_methods(['POST'])
@admin_logged_in
def getReportList(request):
    if checkParameter(['status'], request):
        data = json.loads(request.body)
        status = data['status']

        if not reportStatusValidation(status):
            return resInvalidPara(['status'])

        reports = Report.objects.filter(status=status)
        return resReturn({'result' : [r.body() for r in reports]})
    
    else:
        reports = Report.objects.all()
        return resReturn({'result' : [r.body() for r in reports]})
