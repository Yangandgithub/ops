from django.conf.urls import url, include
from django.contrib import admin
from asset.views import (asset_port, asset_dashboard, asset_hard, ssh_proxy_config,asset_soft)
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url('^port/$', asset_port.asset_port),
    url('^list/$', asset_hard.list_hard),
    url('^hard/list/$', asset_hard.list_hard),
    url('^hard/add/$', asset_hard.add_hard),
    url('^hard/update/$', asset_hard.update_hard),
    url('^hard/delete/$', asset_hard.delete_hard),
    url('^hard/select/$', asset_hard.select_hard),
    url('^hard/selectbyid/$', asset_hard.select_hard_byid),
    url('^dashboard/list/$', asset_dashboard.list_dashboard_hard),
    url('^dashboard/select/$', asset_dashboard.select_dashboard_hard),
    url('^hard/editsshproxy/$', ssh_proxy_config.edit_ssh_proxy_config),
    url('^hard/savesshproxy/$', ssh_proxy_config.save_ssh_proxy_config),
    url('^soft/list/$', asset_soft.list_asset_soft),
]

urlpatterns = format_suffix_patterns(urlpatterns)
