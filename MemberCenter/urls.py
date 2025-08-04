from . import views
from django.urls import path,include
from django.urls import re_path as url

urlpatterns = [
    path('member/', views.member_center_view, name='member_center'),
    path('member/license/add/', views.add_plate_view, name='add_plate'),
    path('member/license/edit/<int:plate_id>/', views.edit_plate_view, name='edit_plate'),
    path('member/license/delete/<int:plate_id>/', views.delete_plate_view, name='delete_plate'),
    path('member/card/edit/', views.edit_card_view, name='edit_card'),
]
