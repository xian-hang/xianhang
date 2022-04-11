from . import views
from django.urls import path

urlpatterns = [
    path('create/', views.createProduct),
    path('<int:id>/', views.product),
    path('<int:id>/edit/', views.editProduct),

]
