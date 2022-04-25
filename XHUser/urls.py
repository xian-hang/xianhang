from . import views
from django.urls import path

urlpatterns = [
    path('request/', views.checkReq),
    path('sendmail/', views.sendEmailTest),

    path('login/', views.userLogin),
    path('logout/', views.userLogout),
    path('create/', views.createUser),
    path('<str:key>/verify/', views.verifyEmail),

    path('<int:id>/', views.getUser),
    path('<int:id>/delete/', views.deacUser),
    path('<int:id>/edit/status/', views.editStatus),
    path('edit/', views.editUser),
    path('edit/password/', views.editPassword),

    path('search/', views.searchUser),
    
    path('<int:id>/product/', views.userProduct),

    path('like/create/', views.createLike),
    path('like/<int:id>/delete/', views.deleteLike),
]
