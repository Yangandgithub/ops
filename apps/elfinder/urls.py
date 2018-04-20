from django.conf.urls import patterns, url
from django.contrib.admin.views.decorators import staff_member_required
from elfinder.views import ElfinderConnectorView
from elfinder.view import roles

urlpatterns = patterns(
    url(r'^yawd-connector/(?P<optionset>.+)/(?P<start_path>.+)/(?P<show_file>.+)/$',
        staff_member_required(ElfinderConnectorView.as_view()),
        name='yawdElfinderConnectorView'),
    url(r'^roles/(?P<optionset>.+)/(?P<start_path>.+)/(?P<show_file>.+)/$',
        ElfinderConnectorView.as_view(),
        name='ElfinderConnector'),
    url(r'^list/$', roles.role_management)
)
