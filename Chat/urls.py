from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.loginTest),
    path('list/', views.getChatList),
    path('room/', views.room),
]