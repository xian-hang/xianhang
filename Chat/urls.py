from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.loginTest),
    path('<str:userId>/', views.room),
]