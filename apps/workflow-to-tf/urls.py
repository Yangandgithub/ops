from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns

from workflow.views import workflow, launch_workflow

urlpatterns = [
    url('^workflow_task/$', workflow, name='workflow'),
    url('^workflow_task_launch/$', launch_workflow, name='launch_workflow')
]

urlpatterns = format_suffix_patterns(urlpatterns)
