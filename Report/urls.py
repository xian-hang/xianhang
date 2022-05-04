from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.createReport),
    path('<int:id>/', views.getReport),
    path('<int:id>/edit/', views.editReport),
    path('list/', views.getReportList),

    path('image/create/',views.createReportImage),
    path('image/<int:id>/url/',views.getReportImageUrl),

    path('notice/create/', views.createReportNotice),
    path('notice/', views.getReportNoticeList),
]
