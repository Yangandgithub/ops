from django.conf.urls import url, include
from django.contrib import admin
from log.views import ansible_log
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url('^ansible/list/$', ansible_log.list_ansible_log),
    url('^ansible/resultsum/$', ansible_log.ansible_playbook_sum),
    url('^ansible/concise/$', ansible_log.ansible_modle_concise),
    url('^ansible/export/$', ansible_log.ansible_modle_export),
    url('^ansible/log/model/$', ansible_log.ansible_model_log),
    url('^ansible/log/playbook/$', ansible_log.ansible_playbook_log),
    url('^ansible/logview/model/$', ansible_log.ansible_model_log_view),
    url('^ansible/logview/playbook/$', ansible_log.ansible_playbook_log_view),
]

urlpatterns = format_suffix_patterns(urlpatterns)
