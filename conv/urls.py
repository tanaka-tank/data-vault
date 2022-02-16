#path関数をインポート
from django.urls import path
from django.urls import include
#同ディレクトリからview.pyをインポート
from .views import ConvIndexView

urlpatterns = [
    path('', ConvIndexView.conv_lcconvert, name='convert_index'),
    path('lcconvert/', ConvIndexView.conv_lcconvert, name='lcconvert'),
    path('clconvert/', ConvIndexView.conv_clconvert, name='clconvert'),
]