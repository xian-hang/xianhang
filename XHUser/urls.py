from . import views
from django.urls import path

urlpatterns = [
    path('request/', views.checkReq),
    path('sendmail/', views.sendEmailTest),

    path('login/', views.userLogin),
    path('logout/', views.userLogout),
    path('create/', views.createUser),
    path('<int:id>/verify/', views.verifyEmail),

    path('<int:id>/', views.user),
    path('<int:id>/edit/', views.editUser),
    path('<int:id>/edit/password/', views.editPassword),
]
