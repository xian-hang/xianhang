from . import views
from django.urls import path

urlpatterns = [
    path('search/', views.searchProduct),
    path('create/', views.createProduct),
    path('<int:id>/', views.getProduct),
    path('<int:id>/edit/', views.editProduct),

]
