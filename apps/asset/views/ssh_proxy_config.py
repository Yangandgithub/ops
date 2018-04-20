#!/usr/bin/env python
# _#_ coding:utf-8 _*_
import uuid, os, json
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from OpsManage.data.DsRedisOps import DsRedis
from django.contrib.auth.decorators import permission_required


@login_required()
def edit_ssh_proxy_config(request):
    if request.method == "POST":
        try:
            ssh_config_filename = "/root/.ssh/config"
            if os.path.exists(ssh_config_filename):
                with open(ssh_config_filename, 'r') as sshconfig:
                    content = sshconfig.read()
                data = {'config_content': content}
            else:
                data = {'config_content': ""}
            return JsonResponse({'msg': "操作成功", "code": 0, 'data': data})
        except Exception, e:
            return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})


@login_required()
def save_ssh_proxy_config(request):
    if request.method == "POST":
        try:
            if DsRedis.OpsAnsiblePlayBookLock.get(
                    redisKey='ssh_config_redis_key -locked') is None:  # 判断/root/.ssh/config是否有人在修改
                # 加上锁
                DsRedis.OpsAnsiblePlayBookLock.set(redisKey='ssh_config_redis_key -locked', value=request.user)
                content = request.POST.get('config_content')
                ssh_config_filename = "/root/.ssh/config"
                with open(ssh_config_filename, 'w') as sshconfig:
                    sshconfig.write(content)
                DsRedis.OpsAnsiblePlayBookLock.delete(redisKey='ssh_config_redis_key -locked')
                return JsonResponse({'msg': "操作成功", "code": 0, 'data': []})
            else:
                return JsonResponse({'msg': "其它用户正在修改代理配置", "code": 500,
                                     'data': []})
        except Exception, e:
            DsRedis.OpsAnsiblePlayBookLock.delete(redisKey='ssh_config_redis_key -locked')
            return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})
