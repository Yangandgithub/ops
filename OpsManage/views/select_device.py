#!/usr/bin/env python
# _#_ coding:utf-8 _*_
import uuid, os, json
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from OpsManage.models import (Server_Assets, TF_Device_Info,
                              TF_Asset_Soft_Info, TF_Asset_Hard_Info,
                              TF_Device_Dynamic_Info, Ansible_CallBack_PlayBook_Result,
                              Ansible_Playbook, Ansible_Playbook_Number,
                              Log_Ansible_Model, Log_Ansible_Playbook, TF_Asset_Port_Info)
from django.contrib.auth.decorators import permission_required
from django.core.paginator import PageNotAnInteger, Paginator, InvalidPage, EmptyPage
from django.contrib.auth.models import User, Group

@login_required()
@permission_required('OpsManage.can_read_tf_device_info', login_url='/noperm/')
def select_device_info(request):
    if request.method == "POST":
        try:
            snippet = TF_Device_Info.objects.all()
            if ((len(request.POST.get('groupId')) > 0) and (int(request.POST.get('groupId')) != 0)):
                snippet = snippet.filter(platform_id=request.POST.get('groupId'))
            if len(request.POST.get('os_type')) > 0:
                snippet = snippet.filter(hardinfo__os_type__contains=request.POST.get('os_type'))
            if len(request.POST.get('middleware_type')) > 0:
                snippet = snippet.filter(softinfo__sw_name__contains=request.POST.get('middleware_type'))
            if len(request.POST.get('db_type')) > 0:
                snippet = snippet.filter(softinfo__sw_name__contains=request.POST.get('db_type'))

            data = []
            data1 = []
            for item in snippet:
                if item.device_id not in data1:
                    res = {
                        'device_id': item.device_id,
                    }
                    data.append(res)
                    data1.append(item.device_id)
            return JsonResponse({"code": 0, 'data': data})
        except Exception, e:
            return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})
