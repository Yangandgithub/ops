from django.conf.urls import url, include
from django.contrib import admin
from crontask.views import cron_task_manage
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url('^task_model/$', cron_task_manage.task_model),
    url('^task_dispatch/$', cron_task_manage.task_dispatch),
    url('^add_crontab/$', cron_task_manage.addCrontab),
    url('^del_crontab/$', cron_task_manage.delCrontab),
    url('^add_interval/$', cron_task_manage.addInterval),
    url('^del_interval/$', cron_task_manage.delInterval),
    url('^add_task/$', cron_task_manage.addTask),
    url('^edit_task/$', cron_task_manage.editTask),
    url('^del_task/$', cron_task_manage.delTask),
]

urlpatterns = format_suffix_patterns(urlpatterns)
