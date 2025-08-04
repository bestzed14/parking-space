from django.contrib import admin
from django.urls import path
from parking_space import views
from django.urls import re_path as url
from django.views.generic import TemplateView, ListView

urlpatterns = [
    path('', views.homepage, name='home'),  # 首頁
    path('get_parking_data/', views.get_parking_data, name='get_parking_data'),
    path('test/', views.test_view, name='test'),
    path('get_merged_parking_data/', views.get_merged_parking_data),
    path('nearby_parking/', views.nearby_parking),
    path('update_PSA_CP/', views.update_PSA_CP, name='update_psa_cp'),
    path('cheapest_nearby_parking/', views.cheapest_nearby_parking),
    path('get_location_info/', views.get_location_info),  
]