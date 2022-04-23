from . import views
from django.urls import path

urlpatterns = [
    path('create/', views.createFollowership),
    path('<int:id>/delete/', views.deleteFollowership),
    path('list/', views.followershipList),
]
