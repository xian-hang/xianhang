from . import views
from django.urls import path

urlpatterns = [
    path('create/', views.createOrder),
    path('<int:id>/', views.getOrder),
    path('<int:id>/edit/', views.editOrder),
    path('<int:id>/edit/status/', views.editOrderStatus),
    path('selling/', views.sellingList),
    path('buying/', views.buyingList),
]
