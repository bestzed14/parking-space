"""
URL configuration for parkingsys project.

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
from django.urls import path,include
from django.urls import re_path as url
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('parking_space.urls')),
    path('EntryPage/', include('EntryPage.urls')),
    path('UserInterface/', include('UserInterface.urls')),
    path('OwnerInterface/', include('OwnerInterface.urls')),
    path('MemberCenter/', include('MemberCenter.urls')),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path(('myapp/'), include('myapp.urls')),
    path('captcha/', include('captcha.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 這行讓 Django 在開發階段能顯示上傳圖片
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
