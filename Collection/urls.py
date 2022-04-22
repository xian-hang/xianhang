from . import views
from django.urls import path

urlpatterns = [
    path('create/', views.createCollection),
    path('<int:id>/delete/', views.deleteCollection),
    path('list/', views.collectionList),
]
