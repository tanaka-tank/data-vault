#path関数をインポート
from django.urls import path
from django.urls import include
#同ディレクトリからview.pyをインポート
from .views import AcoinIndexView

urlpatterns = [
    path('', AcoinIndexView.index, name='acoin_index'),
    path('indexsp/', AcoinIndexView.indexsp, name='acoin_indexsp'),
    path('chart1/', AcoinIndexView.chart1, name='acoin_chart1'),
]