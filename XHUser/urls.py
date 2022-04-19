from . import views
from django.urls import path

urlpatterns = [
    path('request/', views.checkReq),
    path('sendmail/', views.sendEmailTest),

    path('login/', views.userLogin),
    path('logout/', views.userLogout),
    path('create/', views.createUser),
    path('search/', views.searchUser),
    path('<int:id>/verify/', views.verifyEmail),

    path('<int:id>/', views.getUser),
    path('<int:id>/edit/', views.editUser),
    path('<int:id>/edit/password/', views.editPassword),
    path('<int:id>/edit/status/', views.editStatus),
]
