from django.shortcuts import render
from django.http import HttpResponse
from django.utils import html
from django.template.defaultfilters import urlize
from django.views.generic import View
from django.core.exceptions import PermissionDenied
import random
# Create your views here.

class IndexView(View):
    def index(req, *args, **kwargs):
        params = {}
        params["random"] = IndexView.noise()
        return render(req, 'index.html',params)
    
    def index403(req, *args, **kwargs):
        #if not self.request.user.is_authenticated:
        raise PermissionDenied
    
    def noise():
        return str(1 if random.random() >= 0.5 else 2)