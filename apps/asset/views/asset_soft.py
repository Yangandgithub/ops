#!/usr/bin/env python
# _#_ coding:utf-8 _*_
import uuid, os, json
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from OpsManage.models import (TF_Device_Info, TF_Asset_Soft_Info)
from django.contrib.auth.decorators import permission_required
from django.core.paginator import PageNotAnInteger, Paginator, InvalidPage, EmptyPage
from django.contrib.auth.models import User, Group


@login_required()
@permission_required('OpsManage.can_read_tf_asset_soft_info', login_url='/noperm/')
def list_asset_soft(request):
    if request.method == "GET":
        groupList = Group.objects.all()
        return render_to_response('soft/asset_soft_list.html', {"user": request.user, "groupList": groupList},
                                  context_instance=RequestContext(request))
    elif request.method == "POST":
        try:
            iDisplayStart = request.POST.get('iDisplayStart', 0)
            iDisplayLength = request.POST.get('iDisplayLength', 10)
            page = request.POST.get('page')

            softObj = TF_Asset_Soft_Info.objects.all()
            if len(request.POST.get('sw_type')) > 0:
                softObj = softObj.filter(sw_type=request.POST.get('sw_type'))
            if len(request.POST.get('sw_name')) > 0:
                softObj = softObj.filter(sw_name=request.POST.get('sw_name'))

            if len(request.POST.get('device_id')) > 0:
                softObj = softObj.filter(device_id=request.POST.get('device_id'))

            if (len(request.POST.get('platform_id')) > 0) and (int(request.POST.get('platform_id')) != 0):
                softObj = softObj.filter(device_id__platform_id=request.POST.get('platform_id'))

            if len(request.POST.get('ipAdd')) > 0:
                softObj = softObj.filter(device_id__ansible_ssh_host__contains=request.POST.get('ipAdd'))

            paginator = Paginator(softObj, iDisplayLength)  # 设置device在每页显示的数量
            list = paginator.page(page)  # 取页数据

            rest = {
                "iTotalRecords": int(iDisplayStart),  # 本次加载记录数量
                "iTotalDisplayRecords": softObj.count(),  # 总记录数量
                # "sEcho" : sEcho,
                "aaData": []}
            data = []
            for item in list:
                res = {
                    'device_id': item.device_id.device_id,
                    'ansible_ssh_host': item.device_id.ansible_ssh_host,
                    'platform_name': item.device_id.platform_name,
                    # '0:通用软件;  1:应用软件',
                    'sw_type': item.get_sw_type_display(),
                    'sw_name': item.sw_name,
                    'sw_version': item.sw_version,
                    'sw_install_path': item.sw_install_path,
                    'sw_conf_file_path': item.sw_conf_file_path,
                    'record_time': item.record_time
                }
                data.append(res)
            rest['aaData'] = data
            return JsonResponse(rest)
        except Exception, e:
            return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})
