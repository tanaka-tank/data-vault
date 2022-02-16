"""datavault URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
#Include関数をインポート
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('', include('index.urls')),
    path('acoin/', include('acoin.urls')),
    path('odds_avg/', include('odds_avg.urls')),
    path('conv/', include('conv.urls')),
    path('fontimage/', include('fontimage.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
