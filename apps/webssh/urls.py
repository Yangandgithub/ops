from django.conf.urls import url, include
from django.contrib import admin
from webssh.views import webssh
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url('^$', webssh.webssh),
    url('^api/webssh/$', webssh.generate_gate_one_auth_obj),
    url('^websshFrame/(?P<device_id>\S+)/$', webssh.websshFrame),
]

urlpatterns = format_suffix_patterns(urlpatterns)