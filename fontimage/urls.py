#path関数をインポート
from django.urls import path
from django.urls import include
#同ディレクトリからview.pyをインポート
from .views import FontimageIndexView
from .views import FontimageCreateView

urlpatterns = [
    path('', FontimageIndexView.as_view(), name='fontimage_index'),
    path('create/', FontimageCreateView.as_view(), name='fontimage_create'),
    # Ajax処理
    path("exec/", FontimageCreateView.exec_ajax, name='fontimage_exec'),
]