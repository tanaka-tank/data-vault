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
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url

from acoin.views import AcoinIndexView
from odds_avg.views import BoatIndexView
from odds_avg.views import XrentanView
from conv.views import ConvIndexView
from index.views import IndexView

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('', IndexView.index, name='_index'),
    path('403/', IndexView.index403, name='_index403'),
    path('acoin/', AcoinIndexView.index, name='acoin_index'),
    path('indexsp/', AcoinIndexView.indexsp, name='acoin_indexsp'),
    path('acoin/chart1/', AcoinIndexView.chart1, name='acoin_chart1'),
    path('odds_avg/', BoatIndexView.as_view(), name='oddsavg_index'),
    url(r'^odds_avg/(?P<place_name>\w+)/$', XrentanView.as_view(), name='odds_avg_xrentan'),
    path('conv/', ConvIndexView.conv_lcconvert, name='convert_index'),
    path('conv/lcconvert/', ConvIndexView.conv_lcconvert, name='lcconvert'),
    path('conv/clconvert/', ConvIndexView.conv_clconvert, name='clconvert'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
