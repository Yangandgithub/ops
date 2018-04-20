"""OpsManage URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from django.contrib import admin
# from elfinder.views import ElfinderConnectorView
from rest_framework.urlpatterns import format_suffix_patterns
from OpsManage.views import index, ansible, select_device

# from apps.webssh.views import webssh

urlpatterns = [
    url(r'^$', index.index),
    # url(r'^api-auth', include('rest_framework.urls', namespace='rest_framework')),
    # url(r'^admin', admin.site.urls),
    url(r'^verfiyCode$', index.create_code_img),
    url(r'^login', index.login),
    url(r'^logout', index.logout),
    url(r'^config', index.config),
    url(r'^noperm', index.noperm),

    # url(r'^assets_config', assets.assets_config),
    # url(r'^assets_add', assets.assets_add),
    # url(r'^assets_hard_list', assets.asset_hard_info),
    # url(r'^assets_list', assets.assets_list),
    # url(r'^assets_mod/(?P<aid>[0-9]+)/$', assets.assets_modf),
    # url(r'^assets_view/(?P<aid>[0-9]+)/$', assets.assets_view),
    # url(r'^assets_facts', assets.assets_facts),
    # url(r'^assets_log/', assets.assets_log),

    # url(r'^inventory/list/$', tf_device.inventory),
    # url(r'^port/list/$',tf_asset_port.port),
    # url(r'^inventory/hard/list/$', tf_device.inventory_hard),
    # url(r'^inventory/soft/list/$', tf_device.inventory_soft),
    # url(r'^inventory/port/$', tf_device.inventory_port),
    # url(r'^inventory/list/sshconfig', tf_ssh_config.ssh_config),

    # url(r'^cron_add', cron.cron_add),
    # url(r'^cron_list', cron.cron_list),
    # url(r'^cron_config', cron.cron_config),
    # url(r'^cron_log', cron.cron_log),
    # url(r'^cron_mod/(?P<cid>[0-9]+)/$', cron.cron_mod),

    # url(r'^deploy_add', deploy.deploy_add),
    # url(r'^deploy_list', deploy.deploy_list),
    # url(r'^deploy_log', deploy.deploy_log),
    # url(r'^deploy_mod/(?P<pid>[0-9]+)/$', deploy.deploy_modf),
    # url(r'^deploy_init/(?P<pid>[0-9]+)/$', deploy.deploy_init),
    # url(r'^deploy_version/(?P<pid>[0-9]+)/$', deploy.deploy_version),
    # url(r'^deploy_run/(?P<pid>[0-9]+)/$', deploy.deploy_run),
    # url(r'^deploy_result/(?P<pid>[0-9]+)/$', deploy.deploy_result),
    # url(r'^deploy_ask/(?P<pid>[0-9]+)/$', deploy.deploy_ask),
    # url(r'^deploy_order/$', deploy.deploy_order),
    # url(r'^deploy_order/status/(?P<pid>[0-9]+)/$', deploy.deploy_order_status),
    # url(r'^deploy_order/rollback/(?P<pid>[0-9]+)/$', deploy.deploy_order_rollback),
    # url(r'^deploy_manage/(?P<pid>[0-9]+)/$', deploy.deploy_manage),

    url(r'^apps/$', ansible.apps_list_new),
    url(r'^apps/model/$', ansible.apps_model_new),
    url(r'^apps/run/$', ansible.ansible_run),
    # url(r'^apps/log/$', ansible.ansible_log),
    # url(r'^apps/log/(?P<model>[a-z]+)/(?P<id>[0-9]+)/$', ansible.ansible_log_view),
    url(r'^apps/playbook/add/$', ansible.apps_add_new1),
    url(r'^apps/playbook/file/(?P<pid>[0-9]+)/$', ansible.apps_playbook_file_new),
    url(r'^apps/playbook/file1/$', ansible.apps_playbook_file_new1),
    url(r'^apps/playbook/run/(?P<pid>[0-9]+)/$', ansible.apps_playbook_run_new),
    url(r'^apps/playbook/modf/(?P<pid>[0-9]+)/$', ansible.apps_playbook_modf_new),
    # url(r'^apps/tf/asset/soft/$', assets.asset_soft_info),
    # url(r'^apps/tf/asset/hard/$', assets.asset_hard_info),
    url(r'^playbook/list$', ansible.playbook_list_new),
    url(r'^apps/upload', ansible.upload),
    # url(r'^apps/log/resultsum/$', tf_playbook_sum.apps_playbook_sum),
    # url(r'^apps/log/concise/$', tf_playbook_sum.apps_modle_Concise),
    # url(r'^apps/log/export/$', tf_playbook_sum.apps_modle_export),
    url(r'^apps/model/deviceInfo', select_device.select_device_info),

    # url(r'^users/manage/$', users.user_manage),
    # url(r'^register/', users.register),
    # url(r'^user/(?P<uid>[0-9]+)/$', users.user),
    # url(r'^user/center/$', users.user_center),
    # url(r'^group/(?P<gid>[0-9]+)/$', users.group),

    # url(r'^api/assets/$', assets_api.asset_list),
    # url(r'^api/assets/(?P<id>[0-9]+)/$', assets_api.asset_detail),
    # url(r'^api/service/$', assets_api.service_list),
    # url(r'^api/service/(?P<id>[0-9]+)/$', assets_api.service_detail),
    # url(r'^api/group/$', assets_api.group_list),
    # url(r'^api/group/(?P<id>[0-9]+)/$', assets_api.group_detail),
    # url(r'^api/user/$', users_api.user_list),
    # url(r'^api/user/(?P<id>[0-9]+)/$', users_api.user_detail),
    # url(r'^api/zone/$', assets_api.zone_list),
    # url(r'^api/zone/(?P<id>[0-9]+)/$', assets_api.zone_detail),
    # url(r'^api/line/$', assets_api.line_list),
    # url(r'^api/line/(?P<id>[0-9]+)/$', assets_api.line_detail),
    # url(r'^api/raid/$', assets_api.raid_list),
    # url(r'^api/raid/(?P<id>[0-9]+)/$', assets_api.raid_detail),
    # url(r'^api/server/$', assets_api.asset_server_list),
    # url(r'^api/server/(?P<id>[0-9]+)/$', assets_api.asset_server_detail),
    # url(r'^api/net/$', assets_api.asset_net_list),
    # url(r'^api/net/(?P<id>[0-9]+)/$', assets_api.asset_net_detail),
    # url(r'^api/cron/$', cron_api.cron_list),
    # url(r'^api/cron/(?P<id>[0-9]+)/$', cron_api.cron_detail),
    # url(r'^api/deploy/$', deploy_api.deploy_list),
    # url(r'^api/deploy/(?P<id>[0-9]+)/$', deploy_api.deploy_detail),
    # url(r'^api/playbook/$', ansible_api.playbook_list),
    # url(r'^api/playbook/(?P<id>[0-9]+)/$', ansible_api.playbook_detail),
    # url(r'^api/order/(?P<username>.+)/$', deploy_api.OrderList.as_view()),
    # url(r'^api/logs/assets/(?P<id>[0-9]+)/$', assets_api.assetsLog_detail),
    # url(r'^api/logs/cron/(?P<id>[0-9]+)/$', cron_api.cronLogsdetail),
    # url(r'^api/logs/ansible/model/(?P<id>[0-9]+)/$', ansible_api.modelLogsdetail),
    # url(r'^api/logs/ansible/playbook/(?P<id>[0-9]+)/$', ansible_api.playbookLogsdetail),
    # url(r'^api/logs/deploy/(?P<id>[0-9]+)/$', deploy_api.deployLogs_detail),
    # url(r'^api/tf/asset/hardnum/$', tf_device_api.tf_asset_hard_num),
    # url(r'^api/tf/asset/softnum/(.+)/$', tf_asset_api.tf_asset_soft_num),
    # url(r'^api/tf/asset/softname/(.+)/$', tf_asset_api.tf_asset_soft_name),
    # url(r'^api/tf/asset/hardinfo/(.+)/$', tf_device_api.tf_asset_hard_info),
    # url(r'^api/tf/asset/dynamicinfo/(.+)/$', tf_device_api.tf_device_dynamic_info),
    # url(r'^api/tf/asset/deviceinfo/(.+)/$', tf_device_api.tf_device_info),
    # url(r'^api/tf/playbook/playbookinfo/(.+)/$', tf_playbook_api.tf_playbook_config),

    # url('^api/webssh/$', webssh.generate_gate_one_auth_obj),
    # url('^webssh/$', webssh.webssh),
    # url('^websshFrame/(?P<device_id>\S+)/$', webssh.websshFrame),
    url(r'^webssh/', include('webssh.urls', namespace="webssh")),
    url(r'^asset/', include('asset.urls', namespace="asset")),
    url(r'^log/', include('log.urls', namespace="log")),
    url(r'^api/', include('api.urls', namespace="api")),
    url(r'^users/', include('users.urls', namespace="users")),

    # Add for web ansible role tree management
    url(r'^roles/', include('elfinder.urls', namespace="elfinder")),
    url(r'^crontask/', include('crontask.urls', namespace="crontask")),

    # url(r'^apps/roles/(?P<optionset>.+)/(?P<start_path>.+)/(?P<show_file>.+)/$', ElfinderConnectorView.as_view(),
    #     name='ElfinderConnector'),
    # url(r'^apps/roles/$', ansible.role_management)
    url(r'^workflow/', include('workflow.urls', namespace='workflow')),
]

# urlpatterns = format_suffix_patterns(urlpatterns)
