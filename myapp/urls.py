"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import re_path as url,path
from django.views.generic import TemplateView

from myapp import views

urlpatterns = [
    url(r'^map/', views.map, name='map'),
    url(r'^geocode_address/', views.geocode_address, name='geocode_address'),

    url(r'^test/', views.test_view, name='test'),
    url(r'update_PSA_CP/', views.update_PSA_CP, name='update_psa_cp'),
    url(r'get_merged_parking_data/', views.get_merged_parking_data),
    url(r'^nearby_parking/', views.nearby_parking, name='nearby_parking'),
    url(r'^cheapest_nearby_parking/', views.cheapest_nearby_parking, name='cheapest_nearby_parking'),
]
