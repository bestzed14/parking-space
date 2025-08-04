from django.contrib import admin
from django.urls import path,include
from django.urls import re_path as url
from UserInterface import views

urlpatterns = [
     path('dashboard/', views.dashboard_view, name='dashboard'),
]