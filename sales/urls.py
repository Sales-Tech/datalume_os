from django.urls import path
from . import views

urlpatterns = [
    path('new/', views.order_create, name='order_create'),
]