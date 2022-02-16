from django.conf import settings

def constant_text(request):
    return {
        'APP_NAME': 'fontimage',
        'APP_DESCRIPTION': settings.ENV,
    }