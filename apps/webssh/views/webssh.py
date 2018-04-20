#!/usr/bin/env python
# _#_ coding:utf-8 _*_
import time, hmac, hashlib, json
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from OpsManage.models import TF_Device_Info
from django.conf import settings
from django.contrib.auth.models import Group


@login_required(login_url='/login')
def webssh(request, id=None):
    """列出所有ssh主机"""
    try:
        groupList = Group.objects.all()
        device_infos = TF_Device_Info.objects.all()
        return render_to_response('webssh/webssh.html', {"user": request.user,
                                                         "deviceInfoList": device_infos,
                                                         "groupList": groupList})
    except Exception as e:
        print e
        return render_to_response('webssh/webssh.html', {"user": request.user,
                                                         "errorInfo": "你没有权限访问这台服务器！"})


@login_required(login_url='/login')
def websshFrame(request, device_id):
    """弹出某个主机的ssh tab页面"""
    try:
        groupList = Group.objects.all()
        device_info = TF_Device_Info.objects.get(device_id=device_id)
        return render_to_response('webssh/websshFrame.html', {"user": request.user,
                                                              "device_info": device_info,
                                                              "groupList": groupList},
                                  context_instance=RequestContext(request))
    except Exception as e:
        return render_to_response('webssh/websshFrame.html', {"user": request.user, "errorInfo": "你没有权限访问这台服务器！"},
                                  context_instance=RequestContext(request))


@login_required(login_url='/login')
def generate_gate_one_auth_obj(request):
    """GateOne API认证方法实现
    使用当前登录的用户名，因此在gateone的配置中，该用户名的证书需要有权限能够登陆目标远程服务器
    """
    user = request.user.username
    authobj = {
        'api_key': settings.GATEONE_KEY,
        'upn': user,
        'timestamp': str(int(time.time() * 1000)),
        'signature_method': 'HMAC-SHA1',
        'api_version': '1.0'
    }
    my_hash = hmac.new(settings.GATEONE_SECRET, digestmod=hashlib.sha1)
    my_hash.update(authobj['api_key'] + authobj['upn'] + authobj['timestamp'])
    authobj['signature'] = my_hash.hexdigest()
    auth_info_and_server = {"url": settings.GATEONE_SERVER, "auth": authobj}
    valid_json_auth_info = json.dumps(auth_info_and_server)
    return HttpResponse(valid_json_auth_info)

