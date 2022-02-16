#path関数をインポート
from django.urls import path
from django.urls import include
from django.conf.urls import url
#同ディレクトリからview.pyをインポート
from .views import BoatIndexView
from .views import XrentanView

urlpatterns = [
    path('', BoatIndexView.as_view(), name='oddsavg_index'),
    url(r'^(?P<place_name>\w+)/$', XrentanView.as_view(), name='odds_avg_xrentan'),
]