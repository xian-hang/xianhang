from . import views
from django.urls import path

urlpatterns = [
    path('request/', views.checkReq),
    path('sendmail/', views.sendEmailTest),

    path('login/', views.userLogin),
    path('logout/', views.userLogout),
    path('create/', views.createUser),
    path('resent/', views.resentVerificationEmail),
    path('<str:key>/verify/', views.verifyEmail),

    path('forgot/password/', views.forgotPassword),
    path('<str:key>/reset/password/', views.resetPassword),

    path('profile/', views.getProfile),
    path('<int:id>/', views.getUser),
    path('token/<str:key>/', views.getUserWithToken),
    path('<int:id>/edit/status/', views.editStatus),
    path('<int:id>/edit/rating/', views.editRating),
    path('edit/', views.editUser),
    path('delete/', views.deacUser),
    path('edit/password/', views.editPassword),

    path('search/', views.searchUser),
    
    path('<int:id>/product/', views.userProduct),

    path('like/create/', views.createLike),
    path('like/<int:id>/delete/', views.deleteLike),
]
