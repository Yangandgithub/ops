from django.conf.urls import url, include
from django.contrib import admin
from users.views import users
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^manage/$', users.user_manage),
    url(r'^register/', users.register),
    url(r'^user/(?P<uid>[0-9]+)/$', users.user),
    url(r'^center/$', users.user_center),
    url(r'^group/(?P<gid>[0-9]+)/$', users.group),
]

urlpatterns = format_suffix_patterns(urlpatterns)
