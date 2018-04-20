from django.conf.urls import url, include
from django.contrib import admin
from api.views import (ansible_api, tf_asset_api, tf_device_api, tf_playbook_api,users_api)
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^user/$', users_api.user_list),
    url(r'^user/(?P<id>[0-9]+)/$', users_api.user_detail),
    url(r'^playbook/$', ansible_api.playbook_list),
    url(r'^playbook/(?P<id>[0-9]+)/$', ansible_api.playbook_detail),
    url(r'^logs/ansible/model/(?P<id>[0-9]+)/$', ansible_api.modelLogsdetail),
    url(r'^logs/ansible/playbook/(?P<id>[0-9]+)/$', ansible_api.playbookLogsdetail),
    url(r'^tf/asset/hardnum/$', tf_device_api.tf_asset_hard_num),
    url(r'^tf/asset/softnum/(.+)/$', tf_asset_api.tf_asset_soft_num),
    url(r'^tf/asset/softname/(.+)/$', tf_asset_api.tf_asset_soft_name),
    url(r'^tf/asset/hardinfo/(.+)/$', tf_device_api.tf_asset_hard_info),
    url(r'^tf/asset/dynamicinfo/(.+)/$', tf_device_api.tf_device_dynamic_info),
    url(r'^tf/asset/deviceinfo/(.+)/$', tf_device_api.tf_device_info),
    url(r'^tf/playbook/playbookinfo/(.+)/$', tf_playbook_api.tf_playbook_config),
]

urlpatterns = format_suffix_patterns(urlpatterns)
