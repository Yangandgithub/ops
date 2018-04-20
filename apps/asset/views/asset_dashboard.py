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
@permission_required('OpsManage.can_read_tf_asset_hard_info', login_url='/noperm/')
def list_dashboard_hard(request):
    if request.method == "GET":
        groupList = Group.objects.all()
        return render_to_response('hard/dashboard_hard_list.html', {"user": request.user, "groupList": groupList},
                                  context_instance=RequestContext(request))


@login_required()
@permission_required('OpsManage.can_read_tf_asset_hard_info', login_url='/noperm/')
def select_dashboard_hard(request):
    if request.method == "POST":
        try:
            iDisplayStart = request.POST.get('iDisplayStart', 0)
            iDisplayLength = request.POST.get('iDisplayLength', 10)
            page = request.POST.get('page')

            hardObj = TF_Asset_Hard_Info.objects.all()

            if len(request.POST.get('os_type')) > 0:
                hardObj = hardObj.filter(os_type=request.POST.get('os_type'))

            if len(request.POST.get('device_id')) > 0:
                hardObj = hardObj.filter(device_id=request.POST.get('device_id'))

            if (len(request.POST.get('platform_id')) > 0) and (int(request.POST.get('platform_id')) != 0):
                hardObj = hardObj.filter(device_id__platform_id=request.POST.get('platform_id'))

            if len(request.POST.get('ipAdd')) > 0:
                hardObj = hardObj.filter(device_id__ansible_ssh_host__contains=request.POST.get('ipAdd'))

            paginator = Paginator(hardObj, iDisplayLength)  # 设置device在每页显示的数量
            list = paginator.page(page)  # 取页数据

            rest = {
                "iTotalRecords": int(iDisplayStart),  # 本次加载记录数量
                "iTotalDisplayRecords": hardObj.count(),  # 总记录数量
                # "sEcho" : sEcho,
                "aaData": []}
            data = []

            for item in list:
                res = {
                    'asset_id': item.asset_id,
                    'device_id': item.device_id.device_id,
                    'ansible_ssh_host': item.device_id.ansible_ssh_host,
                    'platform_name': item.device_id.platform_name,
                    'os_type': item.os_type,
                    'record_time': item.record_time
                }
                data.append(res)
            rest['aaData'] = data
            return JsonResponse(rest)
        except Exception, e:
            print e
            return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})


@login_required()
@permission_required('OpsManage.can_read_tf_asset_hard_info', login_url='/noperm/')
def select_dashboard_hard_byId(request):
    try:
        snippet = TF_Asset_Hard_Info.objects.get(asset_id=request.POST.get('asset_id'))
        data = {
            'asset_id': snippet.asset_id,
            'device_id': snippet.device_id.device_id,
            'hd_equipment_type': snippet.hd_equipment_type,
            'hd_serial_no': snippet.hd_serial_no,
            'hd_cpu_model': snippet.hd_cpu_model,
            'hd_cpu_count': snippet.hd_cpu_count,
            'hd_per_cpu_thread': snippet.hd_per_cpu_thread,
            'hd_cpu_kernel_count': snippet.hd_cpu_kernel_count,
            'hd_can_max_mem': snippet.hd_can_max_mem,
            'hd_mem_slot_count': snippet.hd_mem_slot_count,
            'hd_mem_count': snippet.hd_mem_count,
            'hd_per_mem_vendor': snippet.hd_per_mem_vendor,
            'hd_per_mem_type': snippet.hd_per_mem_type,
            'hd_per_mem_rate': snippet.hd_per_mem_rate,
            'hd_per_mem_size': snippet.hd_per_mem_size,
            'hd_local_hd_count': snippet.hd_local_hd_count,
            'hd_local_disk_size': snippet.hd_local_disk_size,
            'hd_local_hd_model': snippet.hd_local_hd_model,
            'hd_nwcard_count': snippet.hd_nwcard_count,
            'hd_per_nwcard_mac': snippet.hd_per_nwcard_mac,
            'hd_per_nwcard_ip': snippet.hd_per_nwcard_ip,
            'hd_sper_nwcard_mask': snippet.hd_sper_nwcard_mask,
            'hd_hba_count': snippet.hd_hba_count,
            'hd_per_hba_port': snippet.hd_per_hba_port,
            'hd_per_hba_rate': snippet.hd_per_hba_rate,
            'hd_have_cdrom': snippet.hd_have_cdrom,
            'hd_cdrom_type': snippet.hd_cdrom_type,
            'hd_usb_speed': snippet.hd_usb_speed,
            'os_type': snippet.os_type,
            'os_architecture': snippet.os_architecture,
            'os_version': snippet.os_version,
            'os_file_type': snippet.os_file_type,
            'os_memory_used_rate': snippet.os_memory_used_rate,
            'acl_selinux_state': snippet.acl_selinux_state,
            'record_time': snippet.record_time
        }
        return JsonResponse({'msg': "操作成功", "code": 0, 'data': data})
    except Exception, e:
        return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})
