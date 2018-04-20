#!/usr/bin/env python
# _#_ coding:utf-8 _*_
import uuid, os, json
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from OpsManage.models import (TF_Device_Info, TF_Asset_Hard_Info)
from django.contrib.auth.decorators import permission_required
from django.core.paginator import PageNotAnInteger, Paginator, InvalidPage, EmptyPage
from django.contrib.auth.models import User, Group


@login_required()
@permission_required('OpsManage.can_read_tf_device_info', login_url='/noperm/')
def list_hard(request):
    if request.method == "GET":
        groupList = Group.objects.all()
        return render_to_response('hard/hard_list.html', {"user": request.user, "groupList": groupList},
                                  context_instance=RequestContext(request))


# @login_required()
# @permission_required('OpsManage.can_add_tf_device_info', login_url='/noperm/')
def add_hard(request):
    if request.method == "GET":
        groupList = Group.objects.all()
        return render_to_response('hard/hard_add.html', {"user": request.user, "groupList": groupList},
                                  context_instance=RequestContext(request))
    elif request.method == "POST":
        try:
            snippet = TF_Device_Info.objects.get(device_id=request.POST.get('device_id'))
        except TF_Device_Info.DoesNotExist:
            try:
                TF_Device_Info.objects.create(
                    device_id=request.POST.get('device_id'),
                    platform_id=request.POST.get('platform_id'),
                    platform_name=request.POST.get('platform_name'),
                    ansible_ssh_host=request.POST.get('ansible_ssh_host'),
                    ansible_ssh_port=request.POST.get('ansible_ssh_port'),
                    ansible_ssh_user=request.POST.get('ansible_ssh_user'),
                )
                return JsonResponse({'msg': "操作成功", "code": 0, 'data': []})
            except Exception, e:
                return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})
        return JsonResponse({'msg': "主机已存在", "code": -1, 'data': []})


@login_required()
@permission_required('OpsManage.can_change_tf_device_info', login_url='/noperm/')
def update_hard(request):
    try:
        snippet = TF_Device_Info.objects.get(device_id=request.POST.get('device_id'))
    except TF_Device_Info.DoesNotExist:
        return JsonResponse({'msg': "主机不存在", "code": -1, 'data': []})
    try:
        TF_Device_Info.objects.filter(device_id=request.POST.get('device_id')).update(
            platform_id=request.POST.get('platform_id'),
            platform_name=request.POST.get('platform_name'),
            ansible_ssh_host=request.POST.get('ansible_ssh_host'),
            ansible_ssh_port=request.POST.get('ansible_ssh_port'),
            ansible_ssh_user=request.POST.get('ansible_ssh_user'),
        )
        return JsonResponse({'msg': "操作成功", "code": 0, 'data': []})
    except Exception, e:
        return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})


@login_required()
@permission_required('OpsManage.can_delete_tf_device_info', login_url='/noperm/')
def delete_hard(request):
    try:
        TF_Device_Info.objects.filter(device_id=request.POST.get('device_id')).delete()
        return JsonResponse({'msg': "操作成功", "code": 0, 'data': []})
    except Exception, e:
        return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})


@login_required()
@permission_required('OpsManage.can_read_tf_device_info', login_url='/noperm/')
def select_hard_byid(request):
    try:
        snippet = TF_Device_Info.objects.get(device_id=request.POST.get('device_id'))
        data = {
            'device_id': snippet.device_id,
            'platform_id': snippet.platform_id,
            'ansible_ssh_host': snippet.ansible_ssh_host,
            'ansible_ssh_port': snippet.ansible_ssh_port,
            'ansible_ssh_name': snippet.ansible_ssh_user
        }
        return JsonResponse({'msg': "操作成功", "code": 0, 'data': data})
    except Exception, e:
        print e
        return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})


@login_required()
@permission_required('OpsManage.can_read_tf_device_info', login_url='/noperm/')
def select_hard(request):
    try:
        iDisplayStart = request.POST.get('iDisplayStart', 0)
        iDisplayLength = request.POST.get('iDisplayLength', 10)
        page = request.POST.get('page')
        ipAdd = request.POST.get('ipAdd')
        platform_id = request.POST.get('platform_id')

        device = TF_Device_Info.objects.all()  # 之前需要从models中导入device

        if len(request.POST.get('ipAdd')) > 0:
            device = device.filter(ansible_ssh_host__contains=ipAdd)

        if request.POST.get('platform_id') != '0':
            device = device.filter(platform_id=platform_id)

        total = device.count();

        paginator = Paginator(device, iDisplayLength)  # 设置device在每页显示的数量
        device_list = paginator.page(page)  # 取页数据
        rest = {
            "iTotalRecords": int(iDisplayStart),  # 本次加载记录数量
            "iTotalDisplayRecords": total,  # 总记录数量
            # "sEcho" : sEcho,
            "aaData": []}
        data = []
        for item in device_list:
            os_type = ""
            os_version = ""
            try:
                device = TF_Asset_Hard_Info.objects.get(device_id=item.device_id)
                os_type = device.os_type,
                os_version = device.os_version,
            except TF_Asset_Hard_Info.DoesNotExist:
                os_type = ""
                os_version = ""
            finally:
                res = {
                    'device_id': item.device_id,
                    'platform_id': item.platform_id,
                    'platform_name': item.platform_name,
                    'ansible_ssh_host': item.ansible_ssh_host,
                    'ansible_ssh_port': item.ansible_ssh_port,
                    'ansible_ssh_name': item.ansible_ssh_user,
                    'os_type': os_type,
                    'os_version': os_version,
                }
                data.append(res)
        rest['aaData'] = data
        return JsonResponse(rest)
    except Exception, e:
        return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})
