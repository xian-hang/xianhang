from . import views
from django.urls import path

urlpatterns = [
    path('sendmail/', views.sendEmailTest),
    path('login/', views.login),
    path('logout/', views.logout),
    path('create/', views.createUser),
    path('<int:id>/verify/', views.verifyEmail),

    path('<int:id>/', views.user),
]
