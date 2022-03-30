from . import views
from django.urls import path
from . import views

urlpatterns = [
    path('sendmail/', views.sendEmailTest),
]

