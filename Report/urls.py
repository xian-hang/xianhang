from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.createReport),
    path('<int:id>/', views.getReport),
    path('<int:id>/edit/', views.editReport),
    path('list/', views.getReportList),
]