from . import views
from django.urls import path, include
from django.urls import re_path as url

urlpatterns = [
    path('owner_dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('parking/add/', views.add_parking, name='add_parking'),
    path('parking/edit/<int:pk>/', views.edit_parking, name='edit_parking'),
    path('parking/delete/<int:pk>/', views.delete_parking, name='delete_parking'),
    path('parking/<int:pk>/manage/', views.manage_parking, name='manage_parking'),
]
