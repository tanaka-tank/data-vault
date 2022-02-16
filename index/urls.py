#path関数をインポート
from django.urls import path
from django.urls import include
#同ディレクトリからview.pyをインポート
from .views import IndexView

urlpatterns = [
    path('', IndexView.index, name='_index'),
    path('sitemap/', IndexView.sitemap, name='_sitemap'),
    path('sitemap.xml', IndexView.sitemapxml, name='_sitemap_xml'),
    path('403/', IndexView.index403, name='_index403'),
]