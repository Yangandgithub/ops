#!/usr/bin/env python
# _#_ coding:utf-8 _*_
import uuid, os, json
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from OpsManage.models import  TF_Asset_Port_Info,TF_Device_Info
from django.contrib.auth.decorators import permission_required
from django.core.paginator import PageNotAnInteger, Paginator, InvalidPage, EmptyPage
from django.contrib.auth.models import User, Group

@login_required()
@permission_required('OpsManage.can_read_tf_asset_port_info', login_url='/noperm/')
def asset_port(request):
    if request.method == "GET":
        groupList = Group.objects.all()
        return render_to_response('port/asset_port_list.html', {"user": request.user, "groupList": groupList},
                                  context_instance=RequestContext(request))
    elif request.method == "POST":
        try:
            iDisplayStart = request.POST.get('iDisplayStart', 0)
            iDisplayLength = request.POST.get('iDisplayLength', 10)
            page = request.POST.get('page')

            snippet = TF_Asset_Port_Info.objects.all()
            if len(request.POST.get('platform_id')) > 1:
                snippet = snippet.filter(groupname__contains=request.POST.get('platform_id'))
            if len(request.POST.get('device_id')) > 0:
                snippet = snippet.filter(device=request.POST.get('device_id'))

            paginator = Paginator(snippet, iDisplayLength)  # 设置device在每页显示的数量
            list = paginator.page(page)  # 取页数据

            rest = {
                "iTotalRecords": int(iDisplayStart),  # 本次加载记录数量
                "iTotalDisplayRecords": snippet.count(),  # 总记录数量
                # "sEcho" : sEcho,
                "aaData": []}
            data = []
            for item in list:
                res = {
                    'device_id': item.device.device_id,
                    'platform_name': item.groupname,
                    'stream_type': item.stream_type,
                    'listen_ip': item.listen_ip,
                    'listen_port': item.listen_port,
                    'process': item.process
                }
                data.append(res)
            rest['aaData'] = data
            return JsonResponse(rest)
        except Exception, e:
            return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})