from . import views
from django.urls import path

urlpatterns = [
    path('search/', views.searchProduct),
    path('create/', views.createProduct),
    path('<int:id>/', views.getProduct),
    path('<int:id>/edit/', views.editProduct),
    path('<int:id>/delete/', views.deleteProduct),

    path('image/create/', views.createProductImage),
    path('image/<int:id>/', views.getProductImage),
    path('image/<int:id>/delete/', views.deleteProductImage),

    path('feed/', views.getFeed),
]
