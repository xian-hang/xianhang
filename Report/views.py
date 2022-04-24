import json
from django.shortcuts import render, get_object_or_404
from Report.models import Report, ReportImage
from django.views.decorators.http import require_http_methods
from .form import ReportImageForm

from common.deco import admin_logged_in, user_logged_in
from common.functool import checkParameter, getActiveUser, getReqUser, saveFormOr400
from common.restool import resBadRequest, resFile, resForbidden, resInvalidPara, resMissingPara, resOk, resReturn
from common.validation import descriptionValidation, reportStatusValidation, reportingIdValidation, reportIdValidation

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

    report = Report.objects.create(user=reqUser, description=description, reporting=reporting)
    return resReturn(report.body())


@admin_logged_in
def getReport(request, id):
    report = get_object_or_404(Report, id=id)
    images = ReportImage.objects.filter(report=report)
    return resReturn({'report' : report.body(), 'image' : [i.id for i in images]})


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


@require_http_methods(['POST'])
@user_logged_in
def createReportImage(request):
    try:
        reportId = int(request.POST.get('reportId'))
    except:
        return resInvalidPara(['reportId'])

    if not reportIdValidation(reportId) :
        return resInvalidPara(['reportId'])

    report = Report.objects.get(id=reportId)
    user = getReqUser(request)

    if report.user.id != user.id:
        return resForbidden("User is not allowed to create image for this report.")

    form = ReportImageForm(request.POST, request.FILES)
    image = saveFormOr400(form)
    image.report = report
    image.save()

    return resOk()


@admin_logged_in
def getReportImage(request,id):
    image = get_object_or_404(ReportImage, id=id)
    return resFile(image.image)