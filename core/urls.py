from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import login, logout

app_path = settings.MY_APP_PATH

urlpatterns = [
    # annotate is the root
    url(r'^' + app_path,
        include('annotate.urls', namespace='annotate')),
    # User account handling
    url(r'^' + app_path + 'accounts/login/$',  login),
    url(r'^' + app_path + 'accounts/logout/$', logout),
    # admin
    url(r'^' + app_path + 'admin/', admin.site.urls),
    # social login
    url(r'^' + app_path,
        include('social.apps.django_app.urls', namespace='social')),
]
