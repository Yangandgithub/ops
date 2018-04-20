#!/usr/bin/env python  
# _#_ coding:utf-8 _*_ 
import uuid, os, json
import time
import yaml  # pip install pyyaml the pure python implemention is enough
import tempfile
import subprocess
import datetime
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from OpsManage.models import Server_Assets, TF_Device_Info, TF_Asset_Soft_Info, TF_Asset_Hard_Info, \
    TF_Device_Dynamic_Info, TF_Playbook_Config
from OpsManage.serializers import *
from OpsManage.data.DsRedisOps import DsRedis
from OpsManage.utils.ansible_api_v2 import ANSRunner, playbookforyaml
from django.contrib.auth.models import User, Group
from OpsManage.models import (Ansible_Playbook, Ansible_Playbook_Number,
                              Log_Ansible_Model, Log_Ansible_Playbook,
                              Ansible_CallBack_Model_Result, Service_Assets,
                              Ansible_CallBack_PlayBook_Result, Assets)
from OpsManage.data.DsMySQL import AnsibleRecord
from django.contrib.auth.decorators import permission_required
from django.core.paginator import PageNotAnInteger, Paginator, InvalidPage, EmptyPage
import operator
import functools
import OpsManage.settings as project_settings


@login_required()
@permission_required('OpsManage.can_read_ansible_playbook', login_url='/noperm/')
def apps_model(request):
    if request.method == "GET":
        serverList = Server_Assets.objects.all()
        groupList = Group.objects.all()
        serviceList = Service_Assets.objects.all()
        return render_to_response('apps/apps_model.html', {"user": request.user, "ans_uuid": uuid.uuid4(),
                                                           "serverList": serverList, "groupList": groupList,
                                                           "serviceList": serviceList},
                                  context_instance=RequestContext(request))
    elif request.method == "POST" and request.user.has_perm('OpsManage.can_change_ansible_playbook'):
        resource = []
        sList = []
        if request.POST.get('server_model') in ['service', 'group', 'custom']:
            if request.POST.get('server_model') == 'custom':
                serverList = request.POST.getlist('ansible_server')
                for server in serverList:
                    server_assets = Server_Assets.objects.get(id=server)
                    sList.append(server_assets.ip)
                    if server_assets.keyfile == 1:
                        resource.append({"hostname": server_assets.ip, "port": int(server_assets.port)})
                    else:
                        resource.append({"hostname": server_assets.ip, "port": int(server_assets.port),
                                         "username": server_assets.username, "password": server_assets.passwd})
            elif request.POST.get('server_model') == 'group':
                serverList = Assets.objects.filter(group=request.POST.get('ansible_group'))
                for server in serverList:
                    sList.append(server.server_assets.ip)
                    if server.server_assets.keyfile == 1:
                        resource.append({"hostname": server.server_assets.ip, "port": int(server.server_assets.port)})
                    else:
                        resource.append({"hostname": server.server_assets.ip, "port": int(server.server_assets.port),
                                         "username": server.server_assets.username,
                                         "password": server.server_assets.passwd})
            elif request.POST.get('server_model') == 'service':
                serverList = Assets.objects.filter(business=request.POST.get('ansible_service'))
                for server in serverList:
                    sList.append(server.server_assets.ip)
                    if server.server_assets.keyfile == 1:
                        resource.append({"hostname": server.server_assets.ip, "port": int(server.server_assets.port)})
                    else:
                        resource.append({"hostname": server.server_assets.ip, "port": int(server.server_assets.port),
                                         "username": server.server_assets.username,
                                         "password": server.server_assets.passwd})
            if len(request.POST.get('custom_model')) > 0:
                model_name = request.POST.get('custom_model')
            else:
                model_name = request.POST.get('ansible_model', None)
            if len(sList) > 0:
                redisKey = request.POST.get('ans_uuid')
                logId = AnsibleRecord.Model.insert(user=str(request.user), ans_model=model_name,
                                                   ans_server=','.join(sList),
                                                   ans_args=request.POST.get('ansible_agrs', None))
                DsRedis.OpsAnsibleModel.delete(redisKey)
                DsRedis.OpsAnsibleModel.lpush(redisKey,
                                              "[Start] Ansible Model: {model}  ARGS:{args}".format(model=model_name,
                                                                                                   args=request.POST.get(
                                                                                                       'ansible_agrs',
                                                                                                       "None")))
                ANS = ANSRunner(resource, redisKey, logId)
                ANS.run_model(host_list=sList, module_name=model_name, module_args=request.POST.get('ansible_agrs', ""))
                DsRedis.OpsAnsibleModel.lpush(redisKey, "[Done] Ansible Done.")
                return JsonResponse({'msg': "操作成功", "code": 200, 'data': []})
            else:
                return JsonResponse({'msg': "操作失败，未选择主机或者该分组没有成员", "code": 500, 'data': []})
        else:
            return JsonResponse({'msg': "操作失败，不支持的操作类型", "code": 500, 'data': []})


@login_required()
@permission_required('OpsManage.can_read_ansible_playbook', login_url='/noperm/')
def apps_model_new(request):
    if request.method == "GET":
        serverList = TF_Device_Info.objects.all()
        groupList = Group.objects.all()
        return render_to_response('apps/apps_model.html', {"user": request.user, "ans_uuid": uuid.uuid4(),
                                                           "serverList": serverList, "groupList": groupList},
                                  context_instance=RequestContext(request))
    elif request.method == "POST" and request.user.has_perm('OpsManage.can_change_ansible_playbook'):
        resource = []
        sList = []
        serverList = request.POST.getlist('ansible_server')
        for server in serverList:
            server_assets = TF_Device_Info.objects.filter(device_id=server)
            for iter in server_assets:
                sList.append(iter.device_id)
                resource.append({"hostname": iter.device_id, "ip": iter.ansible_ssh_host,
                                 "port": int(iter.ansible_ssh_port),
                                 "username": iter.ansible_ssh_user})

        if len(request.POST.get('custom_model')) > 0:
            model_name = request.POST.get('custom_model')
        else:
            model_name = request.POST.get('ansible_model', None)
        if len(sList) > 0:
            redisKey = request.POST.get('ans_uuid')
            logId = AnsibleRecord.Model.insert(user=str(request.user), ans_model=model_name,
                                               ans_server=','.join(sList),
                                               ans_args=request.POST.get('ansible_agrs', None))
            DsRedis.OpsAnsibleModel.delete(redisKey)
            DsRedis.OpsAnsibleModel.lpush(redisKey,
                                          "[Start] Ansible Model: {model}  ARGS:{args}".format(model=model_name,
                                                                                               args=request.POST.get(
                                                                                                   'ansible_agrs',
                                                                                                   "None")))
            ANS = ANSRunner(resource, redisKey, logId,isSudo = int(request.POST.get('sudo_type', 0)))
            ANS.run_model(host_list=sList, module_name=model_name, module_args=request.POST.get('ansible_agrs', ""))
            DsRedis.OpsAnsibleModel.lpush(redisKey, "[Done] Ansible Done.")
            return JsonResponse({'msg': "操作成功", "code": 200, 'data': [], 'resource': resource, 'sList': sList})
        else:
            return JsonResponse({'msg': "操作失败，未选择主机或者该分组没有成员", "code": 500, 'data': []})


@login_required()
def ansible_run(request):
    if request.method == "POST":
        redisKey = request.POST.get('ans_uuid')
        msg = DsRedis.OpsAnsibleModel.rpop(redisKey)
        if msg:
            return JsonResponse({'msg': msg, "code": 200, 'data': []})
        else:
            return JsonResponse({'msg': None, "code": 200, 'data': []})


@login_required()
@permission_required('OpsManage.can_add_ansible_playbook', login_url='/noperm/')
def apps_add(request):
    if request.method == "GET":
        serverList = Server_Assets.objects.all()
        groupList = Group.objects.all()
        userList = User.objects.all()
        serviceList = Service_Assets.objects.all()
        return render_to_response('apps/apps_playbook_config.html', {"user": request.user, "userList": userList,
                                                                     "serverList": serverList, "groupList": groupList,
                                                                     "serviceList": serviceList},
                                  context_instance=RequestContext(request))
    elif request.method == "POST":
        sList = []
        if request.POST.get('server_model') in ['service', 'group', 'custom']:
            if request.POST.get('server_model') == 'custom':
                for sid in request.POST.getlist('playbook_server'):
                    server = Server_Assets.objects.get(id=sid)
                    sList.append(server.ip)
                playbook_server_value = None
            elif request.POST.get('server_model') == 'group':
                serverList = Assets.objects.filter(group=request.POST.get('ansible_group'))
                sList = [s.server_assets.ip for s in serverList]
                playbook_server_value = request.POST.get('ansible_group')
            elif request.POST.get('server_model') == 'service':
                serverList = Assets.objects.filter(business=request.POST.get('ansible_service'))
                sList = [s.server_assets.ip for s in serverList]
                playbook_server_value = request.POST.get('ansible_service')
        try:
            playbook = Ansible_Playbook.objects.create(
                playbook_name=request.POST.get('playbook_name'),
                playbook_desc=request.POST.get('playbook_desc'),
                playbook_vars=request.POST.get('playbook_vars'),
                playbook_uuid=uuid.uuid4(),
                playbook_file=request.FILES.get('playbook_file'),
                playbook_server_model=request.POST.get('server_model', 'custom'),
                playbook_server_value=playbook_server_value,
                playbook_auth_group=request.POST.get('playbook_auth_group', 0),
                playbook_auth_user=request.POST.get('playbook_auth_user', 0),
            )
        except Exception, e:
            return render_to_response('apps/apps_playbook_config.html',
                                      {"user": request.user, "errorInfo": "剧本添加错误：%s" % str(e)},
                                      context_instance=RequestContext(request))
        for sip in sList:
            try:
                Ansible_Playbook_Number.objects.create(playbook=playbook, playbook_server=sip)
            except Exception, e:
                playbook.delete()
                return render_to_response('apps/apps_playbook_config.html',
                                          {"user": request.user, "errorInfo": "目标服务器信息添加错误：%s" % str(e)},
                                          context_instance=RequestContext(request))
                # 操作日志异步记录
        AnsibleRecord.PlayBook.insert(user=str(request.user), ans_id=playbook.id, ans_name=playbook.playbook_name,
                                      ans_content="添加Ansible剧本", ans_server=','.join(sList))
        return HttpResponseRedirect('/apps/playbook/add')


@login_required()
@permission_required('OpsManage.can_add_ansible_playbook', login_url='/noperm/')
def apps_add_new(request):
    if request.method == "GET":
        serverList = TF_Device_Info.objects.all()
        groupList = Group.objects.all()
        userList = User.objects.all()
        pbyaml = playbookforyaml()
        playbookList = pbyaml.getallyaml()
        return render_to_response('apps/apps_playbook_config.html', {"user": request.user, "userList": userList,
                                                                     "serverList": serverList, "groupList": groupList,
                                                                     "playbookList": playbookList,
                                                                     },
                                  context_instance=RequestContext(request))
    elif request.method == "POST":
        sList = []
        for sid in request.POST.getlist('playbook_server'):
            server = TF_Device_Info.objects.filter(device_id=sid)
            for iter in server:
                sList.append(iter.device_id)
                # playbook_server_value = None
        try:
            playbook = Ansible_Playbook.objects.create(
                playbook_name=request.POST.get('playbook_name'),
                playbook_desc=request.POST.get('playbook_desc'),
                playbook_vars=request.POST.get('playbook_vars'),
                playbook_uuid=uuid.uuid4(),
                playbook_file=request.POST.get('playbook_file'),
                playbook_server_model=request.POST.get('server_model', 'custom'),
                playbook_server_value=0,
                playbook_auth_group=request.POST.get('playbook_auth_group', 0),
                playbook_auth_user=request.POST.get('playbook_auth_user', 0),
            )
        except Exception, e:
            serverList = TF_Device_Info.objects.all()
            groupList = Group.objects.all()
            userList = User.objects.all()
            return render_to_response('apps/apps_playbook_config.html',
                                      {"user": request.user, "userList": userList,
                                       "serverList": serverList, "groupList": groupList,
                                       "errorInfo": "剧本添加失败"},
                                      context_instance=RequestContext(request))
        for sip in sList:
            try:
                Ansible_Playbook_Number.objects.create(playbook=playbook, playbook_server=sip)
            except Exception, e:
                playbook.delete()
                return render_to_response('apps/apps_playbook_config.html',
                                          {"user": request.user, "errorInfo": "目标服务器信息添加错误：%s" % str(e)},
                                          context_instance=RequestContext(request))
                # 操作日志异步记录
        AnsibleRecord.PlayBook.insert(user=str(request.user), ans_id=playbook.id, ans_name=playbook.playbook_name,
                                      ans_content="添加Ansible剧本", ans_server=','.join(sList))
        return HttpResponseRedirect('/apps/')


@login_required()
@permission_required('OpsManage.can_add_ansible_playbook', login_url='/noperm/')
def apps_add_new1(request):
    if request.method == "GET":
        serverList = TF_Device_Info.objects.all()
        groupList = Group.objects.all()
        userList = User.objects.all()
        print('dsadsadasdsadsada')
        return render_to_response('apps/apps_playbook_config.html',
                                  {"user": request.user, "userList": userList,
                                "serverList": serverList, "groupList": groupList,
                                   },
                                  context_instance=RequestContext(request))
    elif request.method == "POST":
        sList = []
        for sid in request.POST.getlist('playbook_server'):
            server = TF_Device_Info.objects.filter(device_id=sid)
            for iter in server:
                sList.append(iter.device_id)
                # playbook_server_value = None
        sGroup = ''
        for group in request.POST.getlist('playbook_auth_group', '0'):
            sGroup += group
            sGroup += "|"
        try:
            playbook = Ansible_Playbook.objects.create(
                playbook_name=request.POST.get('playbook_name'),
                playbook_desc=request.POST.get('playbook_desc'),
                playbook_vars=request.POST.get('playbook_vars'),
                playbook_uuid=uuid.uuid4(),
                playbook_file=request.POST.get('playbook_file'),
                playbook_server_model=request.POST.get('server_model', 'custom'),
                playbook_server_value=0,
                playbook_auth_group=sGroup,
                playbook_auth_user=request.POST.get('playbook_auth_user', 0),
                playbook_type=request.POST.get('playbook_type'),
                forks=request.POST.get('forks'),
                check=request.POST.get('run_type'),
                playbook_os_type=request.POST.get('os_type'),
                playbook_db_type=request.POST.get('db_type'),
                playbook_middleware_type=request.POST.get('middleware_type'),

            )
        except Exception, e:
            serverList = TF_Device_Info.objects.all()
            groupList = Group.objects.all()
            userList = User.objects.all()
            return render_to_response('apps/apps_playbook_config.html',
                                      {"user": request.user, "userList": userList,
                                       "serverList": serverList, "groupList": groupList,
                                       "errorInfo": "剧本添加失败"},
                                      context_instance=RequestContext(request))
        for sip in sList:
            try:
                Ansible_Playbook_Number.objects.create(playbook=playbook, playbook_server=sip)
            except Exception, e:
                playbook.delete()
                return render_to_response('apps/apps_playbook_config.html',
                                          {"user": request.user, "errorInfo": "目标服务器信息添加错误：%s" % str(e)},
                                          context_instance=RequestContext(request))
                # 操作日志异步记录
        AnsibleRecord.PlayBook.insert(user=str(request.user), ans_id=playbook.id, ans_name=playbook.playbook_name,
                                      ans_content="添加Ansible剧本", ans_server=','.join(sList))
        return HttpResponseRedirect('/apps/')


@login_required()
@permission_required('OpsManage.can_read_ansible_playbook', login_url='/noperm/')
def apps_list(request):
    if request.method == "GET":
        # 获取已登录用户的user id跟group id
        uid = User.objects.get(username=request.user).id
        gList = []
        for group in User.objects.get(username=request.user).groups.values():
            gList.append(group.get('id'))
        # 获取剧本数据列表
        # playbookList = Ansible_Playbook.objects.order_by("-update_time")
        sql = '''SELECT * FROM opsmanage_ansible_playbook order by update_time desc;'''
        playbookList = Ansible_Playbook.objects.raw(sql)
        for ds in playbookList:
            ds.ansible_playbook_number = Ansible_Playbook_Number.objects.filter(playbook=ds)
            # 如果用户在授权组或者是授权用户，设置runid等于项目id
            if ds.playbook_auth_group in gList or ds.playbook_auth_user == uid:
                ds.runid = ds.id
            # 如果剧本没有授权默认所有用户都可以使用
            elif ds.playbook_auth_group == 0 and ds.playbook_auth_user == 0:
                ds.runid = ds.id
        return render_to_response('apps/apps_list.html', {"user": request.user, "playbookList": playbookList, },
                                  context_instance=RequestContext(request))


@login_required()
@permission_required('OpsManage.can_read_ansible_playbook', login_url='/noperm/')
def apps_list_new(request):
    if request.method == "GET":
        # # 获取已登录用户的user id跟group id
        # uid = User.objects.get(username=request.user).id
        # gList = []
        # for group in User.objects.get(username=request.user).groups.values():
        #     gList.append(group.get('id'))
        # # 获取剧本数据列表
        # playbookList = Ansible_Playbook.objects.all().order_by('-update_time')
        # for ds in playbookList:
        #     ds.ansible_playbook_number = Ansible_Playbook_Number.objects.filter(playbook=ds)
        #     # 如果用户在授权组或者是授权用户，设置runid等于项目id
        #     if ds.playbook_auth_group in gList or ds.playbook_auth_user == uid:
        #         ds.runid = ds.id
        #     # 如果剧本没有授权默认所有用户都可以使用
        #     elif ds.playbook_auth_group == 0 and ds.playbook_auth_user == 0:
        #         ds.runid = ds.id
        return render_to_response('apps/apps_list.html', {"user": request.user, },
                                  context_instance=RequestContext(request))
    if request.method == "POST":
        try:
            uid = User.objects.get(username=request.user).id
            gList = []
            for group in User.objects.get(username=request.user).groups.values():
                gList.append(group.get('id'))

            iDisplayStart = request.POST.get('iDisplayStart', 0)
            iDisplayLength = request.POST.get('iDisplayLength', 10)
            page = request.POST.get('page')

            obj = Ansible_Playbook.objects.all()
            # if len(request.POST.get('sw_type')) > 0:
            #     obj = obj.filter(sw_type=request.POST.get('sw_type'))
            # if len(request.POST.get('sw_name')) > 0:
            #     obj = obj.filter(sw_name=request.POST.get('sw_name'))
            if len(request.POST.get('playbook_type')) > 0:
                obj = obj.filter(playbook_type=request.POST.get('playbook_type'))

            if len(request.POST.get('task_name')) > 0:
                obj = obj.filter(playbook_name__contains=request.POST.get('task_name'))

            obj = obj.order_by('-update_time')

            paginator = Paginator(obj, iDisplayLength)  # 设置device在每页显示的数量
            list = paginator.page(page)  # 取页数据

            rest = {
                "iTotalRecords": int(iDisplayStart),  # 本次加载记录数量
                "iTotalDisplayRecords": obj.count(),  # 总记录数量
                "aaData": []}
            data = []

            for item in list:
                numberList = Ansible_Playbook_Number.objects.filter(playbook=item)
                dataNumber = ''
                for number in numberList:
                    dataNumber += str(number.playbook_server) + ','

                # 如果用户在授权组或者是授权用户，设置runid等于项目id
                if item.playbook_auth_group in gList or item.playbook_auth_user == uid:
                    item.runid = item.id
                # 如果剧本没有授权默认所有用户都可以使用
                elif item.playbook_auth_group == 0 and item.playbook_auth_user == 0:
                    item.runid = item.id
                res = {
                    'id': item.id,
                    'playbook_name': item.playbook_name,
                    'playbook_desc': item.playbook_desc,
                    'playbook_vars': item.playbook_vars,
                    'playbook_uuid': item.playbook_uuid,
                    'playbook_server_model': item.playbook_server_model,
                    'playbook_server_value': item.playbook_server_value,
                    'playbook_file': item.playbook_file,
                    'playbook_auth_group': item.playbook_auth_group,
                    'playbook_auth_user': item.playbook_auth_user,
                    'update_time': item.update_time.strftime("%Y/%m/%d %H:%M:%S"),
                    'playbook_number': dataNumber,
                    'runid': item.runid,
                    'playbook_type': item.playbook_type
                }
                data.append(res)
            rest['aaData'] = data
            return JsonResponse(rest)

        except Exception, e:
            print e
            return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})


@login_required()
@permission_required('OpsManage.can_add_ansible_playbook', login_url='/noperm/')
def apps_playbook_file(request, pid):
    try:
        playbook = Ansible_Playbook.objects.get(id=pid)
    except:
        return JsonResponse({'msg': "剧本不存在，可能已经被删除.", "code": 200, 'data': []})
    if request.method == "POST":
        playbook_file = os.getcwd() + '/' + str(playbook.playbook_file)
        if os.path.exists(playbook_file):
            content = ''
            with open(playbook_file, "r") as f:
                for line in f.readlines():
                    content = content + line
            return JsonResponse({'msg': "剧本获取成功", "code": 200, 'data': content})
        else:
            return JsonResponse({'msg': "剧本不存在，可能已经被删除.", "code": 500, 'data': []})


@login_required()
@permission_required('OpsManage.can_add_ansible_playbook', login_url='/noperm/')
def apps_playbook_file_new(request, pid):
    try:
        playbook = Ansible_Playbook.objects.get(id=pid)
    except:
        return JsonResponse({'msg': "剧本不存在，可能已经被删除.", "code": 200, 'data': []})
    if request.method == "POST":
        playbook_file = '/etc/ansible/playbook/' + str(playbook.playbook_file)
        if os.path.exists(playbook_file):
            content = ''
            with open(playbook_file, "r") as f:
                for line in f.readlines():
                    content = content + line
            return JsonResponse({'msg': "剧本获取成功", "code": 200, 'data': content})
        else:
            return JsonResponse({'msg': "剧本不存在，可能已经被删除.", "code": 500, 'data': [], "playbook_file": playbook_file})


@login_required()
@permission_required('OpsManage.can_add_tf_playbook_config', login_url='/noperm/')
def apps_playbook_file_new1(request, pid):
    try:
        playbook = TF_Playbook_Config.objects.get(id=pid)
    except:
        return JsonResponse({'msg': "剧本不存在，可能已经被删除.", "code": 200, 'data': []})
    if request.method == "POST":
        file_path = ''
        if playbook.playbook_path[-1] != '/':
            file_path = playbook.playbook_path + '/' + str(playbook.playbook_file_name)
        else:
            file_path = playbook.playbook_path + str(playbook.playbook_file_name)
        if os.path.exists(file_path):
            content = ''
            with open(file_path, "r") as f:
                for line in f.readlines():
                    content = content + line
            return JsonResponse({'msg': "剧本获取成功", "code": 200, 'data': content})
        else:
            return JsonResponse({'msg': "剧本不存在，可能已经被删除.", "code": 500, 'data': [], "playbook_file": file_path})


@login_required()
@permission_required('OpsManage.can_add_ansible_playbook', login_url='/noperm/')
def apps_playbook_file_new1(request):
    if request.method == "POST":
        fileName = request.POST.get('fileName')
        playbook_file = '/etc/ansible/playbook/' + str(fileName)
        if os.path.exists(playbook_file):
            content = ''
            with open(playbook_file, "r") as f:
                for line in f.readlines():
                    content = content + line
            return JsonResponse({'msg': "剧本获取成功", "code": 200, 'data': content})
        else:
            return JsonResponse({'msg': "剧本不存在，可能已经被删除.", "code": 500, 'data': [], "playbook_file": playbook_file})


@login_required()
@permission_required('OpsManage.can_change_ansible_playbook', login_url='/noperm/')
def apps_playbook_run(request, pid):
    try:
        playbook = Ansible_Playbook.objects.get(id=pid)
        numberList = Ansible_Playbook_Number.objects.filter(playbook=playbook)
        if numberList:
            serverList = []
        else:
            serverList = Server_Assets.objects.all()
    except:
        return render_to_response('apps/apps_playbook.html', {"user": request.user, "ans_uuid": playbook.playbook_uuid,
                                                              "errorInfo": "剧本不存在，可能已经被删除."},
                                  context_instance=RequestContext(request))
    if request.method == "GET":
        return render_to_response('apps/apps_playbook.html', {"user": request.user, "playbook": playbook,
                                                              "serverList": serverList, "numberList": numberList},
                                  context_instance=RequestContext(request))
    elif request.method == "POST":
        if DsRedis.OpsAnsiblePlayBookLock.get(redisKey=playbook.playbook_uuid + '-locked') is None:  # 判断剧本是否有人在执行
            # 加上剧本执行锁
            DsRedis.OpsAnsiblePlayBookLock.set(redisKey=playbook.playbook_uuid + '-locked', value=request.user)
            # 删除旧的执行消息
            DsRedis.OpsAnsiblePlayBook.delete(playbook.playbook_uuid)
            playbook_file = os.getcwd() + '/' + str(playbook.playbook_file)
            sList = []
            resource = []
            if numberList:
                serverList = [s.playbook_server for s in numberList]
            else:
                serverList = request.POST.getlist('playbook_server')
            for server in serverList:
                server_assets = Server_Assets.objects.get(ip=server)
                sList.append(server_assets.ip)
                if server_assets.keyfile == 1:
                    resource.append({"hostname": server_assets.ip, "port": int(server_assets.port)})
                else:
                    resource.append({"hostname": server_assets.ip, "port": int(server_assets.port),
                                     "username": server_assets.username, "password": server_assets.passwd})
            if playbook.playbook_vars:
                playbook_vars = playbook.playbook_vars
            else:
                playbook_vars = request.POST.get('playbook_vars')
            try:
                if len(playbook_vars) == 0:
                    playbook_vars = dict()
                else:
                    playbook_vars = json.loads(playbook_vars)
                playbook_vars['host'] = sList
            except Exception, e:
                DsRedis.OpsAnsiblePlayBookLock.delete(redisKey=playbook.playbook_uuid + '-locked')
                return JsonResponse({'msg': "剧本外部变量不是Json格式", "code": 500, 'data': []})
            logId = AnsibleRecord.PlayBook.insert(user=str(request.user), ans_id=playbook.id,
                                                  ans_name=playbook.playbook_name,
                                                  ans_content="执行Ansible剧本", ans_server=','.join(sList))
            # 执行ansible playbook
            ANS = ANSRunner(resource, redisKey=playbook.playbook_uuid, logId=logId)
            ANS.run_playbook(host_list=sList, playbook_path=playbook_file, extra_vars=playbook_vars)
            # 获取结果
            result = ANS.get_playbook_result()
            dataList = []
            statPer = {
                "unreachable": 0,
                "skipped": 0,
                "changed": 0,
                "ok": 0,
                "failed": 0
            }
            for k, v in result.get('status').items():
                v['host'] = k
                if v.get('failed') > 0 or v.get('unreachable') > 0:
                    v['result'] = 'Failed'
                else:
                    v['result'] = 'Succeed'
                dataList.append(v)
                statPer['unreachable'] = v['unreachable'] + statPer['unreachable']
                statPer['skipped'] = v['skipped'] + statPer['skipped']
                statPer['changed'] = v['changed'] + statPer['changed']
                statPer['failed'] = v['failed'] + statPer['failed']
                statPer['ok'] = v['ok'] + statPer['ok']
            DsRedis.OpsAnsiblePlayBook.lpush(playbook.playbook_uuid, "[Done] Ansible Done.")
            # 切换版本之后取消项目部署锁
            DsRedis.OpsAnsiblePlayBookLock.delete(redisKey=playbook.playbook_uuid + '-locked')
            # 操作日志异步记录
            #             recordAnsiblePlaybook.delay(user=str(request.user),ans_id=playbook.id,ans_name=playbook.playbook_name,
            #                                         ans_content="执行Ansible剧本",uuid=playbook.playbook_uuid,ans_server=','.join(sList))
            return JsonResponse({'msg': "操作成功", "code": 200, 'data': dataList, "statPer": statPer})
        else:
            return JsonResponse({'msg': "剧本执行失败，{user}正在执行该剧本".format(
                user=DsRedis.OpsAnsiblePlayBookLock.get(playbook.playbook_uuid + '-locked')), "code": 500, 'data': []})


@login_required()
@permission_required('OpsManage.can_change_ansible_playbook', login_url='/noperm/')
def apps_playbook_run_new(request, pid):
    try:
        playbook = Ansible_Playbook.objects.get(id=pid)
        numberList = Ansible_Playbook_Number.objects.filter(playbook=playbook)
        if numberList:
            serverList = []
        else:
            # serverList = Server_Assets.objects.all()
            serverList = TF_Device_Info.objects.all()
    except:
        return render_to_response('apps/apps_playbook.html', {"user": request.user, "ans_uuid": playbook.playbook_uuid,
                                                              "errorInfo": "剧本不存在，可能已经被删除."},
                                  context_instance=RequestContext(request))
    if request.method == "GET":
        return render_to_response('apps/apps_playbook.html', {"user": request.user, "playbook": playbook,
                                                              "serverList": serverList, "numberList": numberList},
                                  context_instance=RequestContext(request))
    elif request.method == "POST":
        if DsRedis.OpsAnsiblePlayBookLock.get(redisKey=playbook.playbook_uuid + '-locked') is None:  # 判断剧本是否有人在执行
            # 加上剧本执行锁
            DsRedis.OpsAnsiblePlayBookLock.set(redisKey=playbook.playbook_uuid + '-locked', value=request.user)
            # 删除旧的执行消息
            DsRedis.OpsAnsiblePlayBook.delete(playbook.playbook_uuid)
            playbook_file = '/etc/ansible/playbook/' + str(playbook.playbook_file)
            sList = []
            resource = []
            if numberList:
                serverList = [s.playbook_server for s in numberList]
            else:
                serverList = request.POST.getlist('playbook_server')
            for server in serverList:
                server_assets = TF_Device_Info.objects.filter(device_id=server)
                for iter in server_assets:
                    sList.append(iter.device_id)
                    resource.append({"hostname": iter.device_id, "ip": iter.ansible_ssh_host,
                                     "port": int(iter.ansible_ssh_port),
                                     "username": iter.ansible_ssh_user})
            if playbook.playbook_vars:
                playbook_vars = playbook.playbook_vars
            else:
                playbook_vars = request.POST.get('playbook_vars')
            try:
                if len(playbook_vars) == 0:
                    playbook_vars = dict()
                else:
                    playbook_vars = json.loads(playbook_vars)
                playbook_vars['host'] = sList
            except Exception, e:
                DsRedis.OpsAnsiblePlayBookLock.delete(redisKey=playbook.playbook_uuid + '-locked')
                return JsonResponse({'msg': "剧本外部变量不是Json格式", "code": 500, 'data': []})
            try:
                logId = AnsibleRecord.PlayBook.insert(user=str(request.user), ans_id=playbook.id,
                                                      ans_name=playbook.playbook_name,
                                                      ans_content="执行Ansible剧本", ans_server=','.join(sList))
                # 执行ansible playbook
                # ANS = ANSRunner(resource, redisKey=playbook.playbook_uuid, logId=logId)
                run_type = False
                if playbook.check == 1:
                    run_type = True
                ANS = ANSRunner(resource, redisKey=playbook.playbook_uuid, logId=logId, forks=playbook.forks,
                                check=run_type)
                ANS.run_playbook(host_list=sList, playbook_path=playbook_file, extra_vars=playbook_vars)
                # 获取结果
                result = ANS.get_playbook_result()
                dataList = []
                statPer = {
                    "unreachable": 0,
                    "skipped": 0,
                    "changed": 0,
                    "ok": 0,
                    "failed": 0
                }
                for k, v in result.get('status').items():
                    v['host'] = k
                    if v.get('failed') > 0 or v.get('unreachable') > 0:
                        v['result'] = 'Failed'
                    else:
                        v['result'] = 'Succeed'
                    dataList.append(v)
                    statPer['unreachable'] = v['unreachable'] + statPer['unreachable']
                    statPer['skipped'] = v['skipped'] + statPer['skipped']
                    statPer['changed'] = v['changed'] + statPer['changed']
                    statPer['failed'] = v['failed'] + statPer['failed']
                    statPer['ok'] = v['ok'] + statPer['ok']
                DsRedis.OpsAnsiblePlayBook.lpush(playbook.playbook_uuid, "[Done] Ansible Done.")
                # 切换版本之后取消项目部署锁
            finally:
                DsRedis.OpsAnsiblePlayBookLock.delete(redisKey=playbook.playbook_uuid + '-locked')
            # 操作日志异步记录
            #             recordAnsiblePlaybook.delay(user=str(request.user),ans_id=playbook.id,ans_name=playbook.playbook_name,
            #                                         ans_content="执行Ansible剧本",uuid=playbook.playbook_uuid,ans_server=','.join(sList))
            return JsonResponse(
                {'msg': "操作成功", "code": 200, 'data': dataList, "statPer": statPer, "serverList": serverList})
        else:
            return JsonResponse({'msg': "剧本执行失败，{user}正在执行该剧本".format(
                user=DsRedis.OpsAnsiblePlayBookLock.get(playbook.playbook_uuid + '-locked')), "code": 500, 'data': []})


@login_required()
@permission_required('OpsManage.can_change_ansible_playbook', login_url='/noperm/')
def apps_playbook_modf(request, pid):
    try:
        playbook = Ansible_Playbook.objects.get(id=pid)
        numberList = Ansible_Playbook_Number.objects.filter(playbook=playbook)
    except:
        return render_to_response('apps/apps_playbook_modf.html', {"user": request.user,
                                                                   "errorInfo": "剧本不存在，可能已经被删除."},
                                  context_instance=RequestContext(request))
    if request.method == "GET":
        numberList = [s.playbook_server for s in numberList]
        serverList = Server_Assets.objects.all()
        for ds in serverList:
            if ds.ip in numberList:
                ds.count = 1
            else:
                ds.count = 0
        groupList = Group.objects.all()
        userList = User.objects.all()
        serviceList = Service_Assets.objects.all()
        return render_to_response('apps/apps_playbook_modf.html', {"user": request.user, "userList": userList,
                                                                   "playbook": playbook, "serverList": serverList,
                                                                   "groupList": groupList, "serviceList": serviceList},
                                  context_instance=RequestContext(request))
    elif request.method == "POST":
        sList = []
        if request.POST.get('server_model') in ['service', 'group', 'custom']:
            if request.POST.get('server_model') == 'custom':
                for sid in request.POST.getlist('playbook_server'):
                    server = Server_Assets.objects.get(id=sid)
                    sList.append(server.ip)
                playbook_server_value = None
            elif request.POST.get('server_model') == 'group':
                serverList = Assets.objects.filter(group=request.POST.get('ansible_group'))
                sList = [s.server_assets.ip for s in serverList]
                playbook_server_value = request.POST.get('ansible_group')
            elif request.POST.get('server_model') == 'service':
                serverList = Assets.objects.filter(business=request.POST.get('ansible_service'))
                sList = [s.server_assets.ip for s in serverList]
                playbook_server_value = request.POST.get('ansible_service')
        try:
            Ansible_Playbook.objects.filter(id=pid).update(
                playbook_name=request.POST.get('playbook_name'),
                playbook_desc=request.POST.get('playbook_desc'),
                playbook_vars=request.POST.get('playbook_vars', None),
                playbook_server_model=request.POST.get('server_model', 'custom'),
                playbook_server_value=playbook_server_value,
                playbook_auth_group=request.POST.get('playbook_auth_group', 0),
                playbook_auth_user=request.POST.get('playbook_auth_user', 0),
            )
        except Exception, e:
            return render_to_response('apps/apps_playbook_modf.html',
                                      {"user": request.user, "errorInfo": "剧本添加错误：%s" % str(e)},
                                      context_instance=RequestContext(request))
        if sList:
            tagret_server_list = [s.playbook_server for s in numberList]
            postServerList = []
            for sip in sList:
                try:
                    postServerList.append(sip)
                    if sip not in tagret_server_list:
                        Ansible_Playbook_Number.objects.create(playbook=playbook, playbook_server=sip)
                except Exception, e:
                    print e
                    return render_to_response('apps/apps_playbook_modf.html', {"user": request.user,
                                                                               "errorInfo": "目标服务器信息修改错误：%s" % str(e)},
                                              context_instance=RequestContext(request))
                    # 清除目标主机 -
            delList = list(set(tagret_server_list).difference(set(postServerList)))
            for ip in delList:
                Ansible_Playbook_Number.objects.filter(playbook=playbook, playbook_server=ip).delete()
        else:
            for server in numberList:
                Ansible_Playbook_Number.objects.filter(playbook=playbook,
                                                       playbook_server=server.playbook_server).delete()
        AnsibleRecord.PlayBook.insert(user=str(request.user), ans_id=playbook.id, ans_name=playbook.playbook_name,
                                      ans_content="修改Ansible剧本", ans_server=None)
        return HttpResponseRedirect('/apps/playbook/modf/{id}/'.format(id=pid))


@login_required()
@permission_required('OpsManage.can_change_ansible_playbook', login_url='/noperm/')
def apps_playbook_modf_new(request, pid):
    try:
        playbook = Ansible_Playbook.objects.get(id=pid)
        numberList = Ansible_Playbook_Number.objects.filter(playbook=playbook)
    except:
        return render_to_response('apps/apps_playbook_modf.html', {"user": request.user,
                                                                   "errorInfo": "剧本不存在，可能已经被删除."},
                                  context_instance=RequestContext(request))
    if request.method == "GET":
        numberList = [s.playbook_server for s in numberList]
        server_data = []
        group_data = []
        grouplist = Group.objects.all()
        for item in grouplist:
            res = {
                'id': item.id,
                'name': item.name,
                'count': 0
            }
            group_data.append(res)
        groupIDList = []

        playbook.playbook_auth_group = playbook.playbook_auth_group.rstrip("|")
        if playbook.playbook_auth_group.find("|") == -1:
            if int(playbook.playbook_auth_group) != 0:
                groupIDList.append(playbook.playbook_auth_group)
        else:
            for group in playbook.playbook_auth_group.split("|"):
                groupIDList.append(group)

        server_data1 = []
        if len(groupIDList) <= 0:
            snippet = TF_Device_Info.objects.all()
            if len(playbook.playbook_os_type.strip()) > 0:
                snippet = snippet.filter(hardinfo__os_type__contains=playbook.playbook_os_type)
            if len(playbook.playbook_db_type.strip()) > 0:
                snippet = snippet.filter(softinfo__sw_name__contains=playbook.playbook_db_type)
            if len(playbook.playbook_middleware_type.strip()) > 0:
                snippet = snippet.filter(softinfo__sw_name__contains=playbook.playbook_middleware_type)
            for ds in snippet:
                if ((ds.device_id in numberList) and (ds.device_id not in server_data1)):
                    res = {
                        'device_id': ds.device_id,
                        'count': 1
                    }
                    server_data.append(res)
                    server_data1.append(ds.device_id)
                elif ds.device_id not in server_data1:
                    res = {
                        'device_id': ds.device_id,
                        'count': 0
                    }
                    server_data.append(res)
                    server_data1.append(ds.device_id)
        else:
            for ds in groupIDList:
                snippet = TF_Device_Info.objects.filter(platform_id=int(ds))
                if len(playbook.playbook_os_type.strip()) > 0:
                    snippet = snippet.filter(hardinfo__os_type__contains=playbook.playbook_os_type)
                if len(playbook.playbook_db_type.strip()) > 0:
                    snippet = snippet.filter(softinfo__sw_name__contains=playbook.playbook_db_type)
                if len(playbook.playbook_middleware_type.strip()) > 0:
                    snippet = snippet.filter(softinfo__sw_name__contains=playbook.playbook_middleware_type)
                for ds in snippet:
                    if ((ds.device_id in numberList) and (ds.device_id not in server_data1)):
                        res = {
                            'device_id': ds.device_id,
                            'count': 1
                        }
                        server_data.append(res)
                        server_data1.append(ds.device_id)
                    elif ds.device_id not in server_data1:
                        res = {
                            'device_id': ds.device_id,
                            'count': 0
                        }
                        server_data.append(res)
                        server_data1.append(ds.device_id)

        for ds in group_data:
            if str(ds['id']) in groupIDList:
                ds['count'] = 1

        playbook_data = {
            'id': playbook.id,
            'playbook_name': playbook.playbook_name,
            'playbook_desc': playbook.playbook_desc,
            'playbook_vars': playbook.playbook_vars,
            'playbook_uuid': playbook.playbook_uuid,
            'playbook_server_model': playbook.playbook_server_model,
            'playbook_server_value': playbook.playbook_server_value,
            'playbook_file': playbook.playbook_file,
            'playbook_auth_group': playbook.playbook_auth_group[0],
            'playbook_auth_user': playbook.playbook_auth_user,
            'playbook_type': playbook.playbook_type,
            'forks': playbook.forks,
            'check': playbook.check,
            'playbook_os_type': playbook.playbook_os_type,
            'playbook_db_type': playbook.playbook_db_type,
            'playbook_middleware_type': playbook.playbook_middleware_type
        }
        userList = User.objects.all()
        return render_to_response('apps/apps_playbook_modf.html', {"user": request.user, "userList": userList,
                                                                   "playbook": playbook_data, "serverList": server_data,
                                                                   "groupList": group_data, "isSuccess": "false"},
                                  context_instance=RequestContext(request))
    elif request.method == "POST":
        sList = []
        for sid in request.POST.getlist('playbook_server'):
            server = TF_Device_Info.objects.filter(device_id=sid)
            for iter in server:
                sList.append(iter.device_id)
        sGroup = ''
        for group in request.POST.getlist('playbook_auth_group', '0'):
            sGroup += group
            sGroup += "|"
        try:
            Ansible_Playbook.objects.filter(id=pid).update(
                playbook_name=request.POST.get('playbook_name'),
                playbook_desc=request.POST.get('playbook_desc'),
                playbook_vars=request.POST.get('playbook_vars', None),
                playbook_server_model=request.POST.get('server_model', 'custom'),
                playbook_auth_group=sGroup,
                playbook_auth_user=request.POST.get('playbook_auth_user', 0),
                playbook_os_type=request.POST.get('os_type'),
                playbook_db_type=request.POST.get('db_type'),
                playbook_middleware_type=request.POST.get('middleware_type'),
                forks=request.POST.get('forks'),
                check=request.POST.get('run_type'),
            )
        except Exception, e:
            numberList = [s.playbook_server for s in numberList]
            serverList = TF_Device_Info.objects.filter(platform_id=playbook.playbook_auth_group)
            for ds in serverList:
                if ds.device_id in numberList:
                    ds.count = 1
                else:
                    ds.count = 0
            groupList = Group.objects.all()
            userList = User.objects.all()
            return render_to_response('apps/apps_playbook_modf.html', {"user": request.user, "userList": userList,
                                                                       "playbook": playbook, "serverList": serverList,
                                                                       "groupList": groupList,
                                                                       "errorInfo": "任务名称重复"},
                                      context_instance=RequestContext(request))
        if sList:
            tagret_server_list = [s.playbook_server for s in numberList]
            postServerList = []
            for sip in sList:
                try:
                    postServerList.append(sip)
                    if sip not in tagret_server_list:
                        Ansible_Playbook_Number.objects.create(playbook=playbook, playbook_server=sip)
                except Exception, e:
                    print e
                    return render_to_response('apps/apps_playbook_modf.html', {"user": request.user,
                                                                               "errorInfo": "目标服务器信息修改错误：%s" % str(e)},
                                              context_instance=RequestContext(request))
                    # 清除目标主机 -
            delList = list(set(tagret_server_list).difference(set(postServerList)))
            for ip in delList:
                Ansible_Playbook_Number.objects.filter(playbook=playbook, playbook_server=ip).delete()
        else:
            for server in numberList:
                Ansible_Playbook_Number.objects.filter(playbook=playbook,
                                                       playbook_server=server.playbook_server).delete()
        AnsibleRecord.PlayBook.insert(user=str(request.user), ans_id=playbook.id, ans_name=playbook.playbook_name,
                                      ans_content="修改Ansible剧本", ans_server=None)
        # return HttpResponseRedirect('/apps/playbook/modf/{id}/'.format(id=pid))
        return HttpResponseRedirect('/apps')


@login_required(login_url='/login')
def ansible_log(request):
    if request.method == "GET":
        return render_to_response('apps/apps_log.html', {"user": request.user},
                                  context_instance=RequestContext(request))
    if request.method == "POST":
        mode = request.POST.get('mode')
        if mode == 'Model':
            try:
                iDisplayStart = request.POST.get('iDisplayStart', 0)
                iDisplayLength = request.POST.get('iDisplayLength', 10)
                page = request.POST.get('page')

                obj = Log_Ansible_Model.objects.all()
                if 'dateRange' in request.POST:
                    dateRange = request.POST.get('dateRange')
                    dataArray = dateRange.split(' - ')
                    dataForm = dataArray[0].split('/')
                    dataTo = dataArray[1].split('/')

                    dataFormYear = dataForm[0]
                    dataFormMonth = dataForm[1]
                    dataFormDay = dataForm[2]

                    dataToYear = dataTo[0]
                    dataToMonth = dataTo[1]
                    dataToDay = dataTo[2]

                    obj = obj.filter(create_time__range=(
                        datetime.datetime(int(dataFormYear), int(dataFormMonth), int(dataFormDay), 0, 0),
                        datetime.datetime(int(dataToYear), int(dataToMonth), int(dataToDay), 23, 59)))

                obj = obj.order_by('-create_time')

                paginator = Paginator(obj, iDisplayLength)  # 设置device在每页显示的数量
                list = paginator.page(page)  # 取页数据

                rest = {
                    "iTotalRecords": int(iDisplayStart),  # 本次加载记录数量
                    "iTotalDisplayRecords": obj.count(),  # 总记录数量
                    "aaData": []}
                data = []

                for item in list:
                    res = {
                        'id': item.id,
                        'ans_user': item.ans_user,
                        'ans_model': item.ans_model,
                        'ans_args': item.ans_args,
                        'ans_server': item.ans_server,
                        'create_time': item.create_time.strftime("%Y/%m/%d %H:%M:%S")
                    }
                    data.append(res)

                rest['aaData'] = data
                return JsonResponse(rest)

            except Exception, e:
                print e
                return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})
        elif mode == 'Playbook':
            try:
                iDisplayStart = request.POST.get('iDisplayStart', 0)
                iDisplayLength = request.POST.get('iDisplayLength', 10)
                page = request.POST.get('page')

                obj = Log_Ansible_Playbook.objects.all()
                if 'dateRange' in request.POST:
                    dateRange = request.POST.get('dateRange')
                    dataArray = dateRange.split(' - ')
                    dataForm = dataArray[0].split('/')
                    dataTo = dataArray[1].split('/')

                    dataFormYear = dataForm[0]
                    dataFormMonth = dataForm[1]
                    dataFormDay = dataForm[2]

                    dataToYear = dataTo[0]
                    dataToMonth = dataTo[1]
                    dataToDay = dataTo[2]

                    obj = obj.filter(create_time__range=(
                        datetime.datetime(int(dataFormYear), int(dataFormMonth), int(dataFormDay), 0, 0),
                        datetime.datetime(int(dataToYear), int(dataToMonth), int(dataToDay), 23, 59)))

                obj = obj.order_by('-create_time')

                paginator = Paginator(obj, iDisplayLength)  # 设置device在每页显示的数量
                list = paginator.page(page)  # 取页数据

                rest = {
                    "iTotalRecords": int(iDisplayStart),  # 本次加载记录数量
                    "iTotalDisplayRecords": obj.count(),  # 总记录数量
                    "aaData": []}
                data = []

                for item in list:
                    res = {
                        'id': item.id,
                        'ans_id': item.ans_id,
                        'ans_user': item.ans_user,
                        'ans_name': item.ans_name,
                        'ans_content': item.ans_content,
                        'ans_server': item.ans_server,
                        'create_time': item.create_time.strftime("%Y/%m/%d %H:%M:%S")
                    }
                    data.append(res)

                rest['aaData'] = data
                return JsonResponse(rest)

            except Exception, e:
                print e
                return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})


@login_required(login_url='/login')
def ansible_log_view(request, model, id):
    if request.method == "POST":
        if model == 'model':
            try:
                result = ''
                logId = Log_Ansible_Model.objects.get(id=id)
                for ds in Ansible_CallBack_Model_Result.objects.filter(logId=logId):
                    result += ds.content
                    result += '\n'
            except Exception, e:
                return JsonResponse({'msg': "查看失败", "code": 500, 'data': e})
        elif model == 'playbook':
            try:
                result = ''
                logId = Log_Ansible_Playbook.objects.get(id=id)
                for ds in Ansible_CallBack_PlayBook_Result.objects.filter(logId=logId):
                    result += ds.content
                    result += '\n'
            except Exception, e:
                return JsonResponse({'msg': "查看失败", "code": 500, 'data': e})
        return JsonResponse({'msg': "操作成功", "code": 200, 'data': result})


@login_required()
@permission_required('OpsManage.can_read_tf_device_info', login_url='/noperm/')
def playbook_list(request):
    if request.method == "GET":
        return render_to_response('apps/playbook_list.html', {"user": request.user},
                                  context_instance=RequestContext(request))
    elif request.method == "POST":
        mode = request.POST.get('mode')
        if mode == 'add':
            # try:
            #     snippet = TF_Playbook_Config.objects.get(device_id=request.POST.get('device_id'))
            # except TF_Device_Info.DoesNotExist:
            try:
                TF_Playbook_Config.objects.create(
                    playbook_name=request.POST.get('playbook_name'),
                    playbook_desc=request.POST.get('playbook_desc'),
                    playbook_path=request.POST.get('playbook_path'),
                    playbook_file_name=request.POST.get('playbook_file_name'),
                    playbook_type=request.POST.get('playbook_type'),
                )
                return JsonResponse({'msg': "操作成功", "code": 0, 'data': []})
            except Exception, e:
                print e
                return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})
        elif mode == 'update':
            try:
                snippet = TF_Playbook_Config.objects.get(id=request.POST.get('id'))
            except TF_Playbook_Config.DoesNotExist:
                return JsonResponse({'msg': "主机不存在", "code": -1, 'data': []})

            try:
                TF_Playbook_Config.objects.filter(id=request.POST.get('id')).update(
                    playbook_name=request.POST.get('playbook_name'),
                    playbook_desc=request.POST.get('playbook_desc'),
                    playbook_path=request.POST.get('playbook_path'),
                    playbook_file_name=request.POST.get('playbook_file_name'),
                    playbook_type=request.POST.get('playbook_type'),
                )
                return JsonResponse({'msg': "操作成功", "code": 0, 'data': []})
            except Exception, e:
                return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})
        elif mode == 'delete':
            try:
                print request.POST.get('id')
                TF_Playbook_Config.objects.filter(id=request.POST.get('id')).delete()
                return JsonResponse({'msg': "操作成功", "code": 0, 'data': []})
            except Exception, e:
                print e
                return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})
        elif mode == 'byId':
            try:
                snippet = TF_Playbook_Config.objects.get(id=request.POST.get('id'))
                data = {
                    'id': snippet.id,
                    'playbook_name': snippet.playbook_name,
                    'playbook_desc': snippet.playbook_desc,
                    'playbook_path': snippet.playbook_path,
                    'playbook_file_name': snippet.playbook_file_name,
                    'playbook_type': snippet.playbook_type,
                    'update_time': snippet.update_time
                }
                return JsonResponse({'msg': "操作成功", "code": 0, 'data': data})
            except Exception, e:
                print e
                return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})

        elif mode == 'select':
            try:
                iDisplayStart = request.POST.get('iDisplayStart', 0)
                iDisplayLength = request.POST.get('iDisplayLength', 10)
                page = request.POST.get('page')
                obj = TF_Playbook_Config.objects.all()  # 之前需要从models中导入device

                if len(request.POST.get('playbook_type')) > 0:
                    obj = obj.filter(playbook_type=request.POST.get('playbook_type'))

                if len(request.POST.get('playbook_name')) > 0:
                    obj = obj.filter(playbook_name__contains=request.POST.get('playbook_name'))

                if len(request.POST.get('playbook_file_name')) > 0:
                    obj = obj.filter(playbook_file_name__contains=request.POST.get('playbook_file_name'))

                total = obj.count();

                paginator = Paginator(obj, iDisplayLength)  # 设置device在每页显示的数量
                list = paginator.page(page)  # 取页数据
                rest = {
                    "iTotalRecords": int(iDisplayStart),  # 本次加载记录数量
                    "iTotalDisplayRecords": total,  # 总记录数量
                    # "sEcho" : sEcho,
                    "aaData": []}
                data = []

                for item in list:
                    res = {
                        'id': item.id,
                        'playbook_name': item.playbook_name,
                        'playbook_desc': item.playbook_desc,
                        'playbook_path': item.playbook_path,
                        'playbook_file_name': item.playbook_file_name,
                        'playbook_type': item.playbook_type,
                        'update_time': item.update_time
                    }
                    data.append(res)
                rest['aaData'] = data
                return JsonResponse(rest)
            except Exception, e:
                print '============== ======error'
                print e
                return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})
        else:
            return render_to_response('inventory/inventory_list.html', {"user": request.user,
                                                                        "errorInfo": "mode illegal "},
                                      context_instance=RequestContext(request))


@login_required()
@permission_required('OpsManage.can_read_tf_device_info', login_url='/noperm/')
def playbook_list_new(request):
    if request.method == "GET":
        return render_to_response('apps/playbook_list.html', {"user": request.user},
                                  context_instance=RequestContext(request))
    elif request.method == "POST":
        mode = request.POST.get('mode')
        if mode == 'add':
            # try:
            #     snippet = TF_Playbook_Config.objects.get(device_id=request.POST.get('device_id'))
            # except TF_Device_Info.DoesNotExist:
            try:
                new_playbook = TF_Playbook_Config.objects.create(
                    playbook_name=request.POST.get('playbook_name'),
                    playbook_desc=request.POST.get('playbook_desc'),
                    playbook_path=request.POST.get('playbook_path'),
                    playbook_file_name=request.POST.get('playbook_file_name'),
                    playbook_type=request.POST.get('playbook_type'),
                )
                playbook_content = request.POST.get('playbook_content')
                if playbook_content:
                    playbook_path = new_playbook.playbook_path
                    playbook_file_name = new_playbook.playbook_file_name
                    location = os.path.join(playbook_path, playbook_file_name)
                    with open(location, 'w') as playbook:
                        playbook.write(playbook_content)
                return JsonResponse({'msg': "操作成功", "code": 0, 'data': []})
            except Exception, e:
                print e
                return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})
        elif mode == 'update':
            try:
                snippet = TF_Playbook_Config.objects.get(id=request.POST.get('id'))
            except TF_Playbook_Config.DoesNotExist:
                return JsonResponse({'msg': "主机不存在", "code": -1, 'data': []})

            try:
                TF_Playbook_Config.objects.filter(id=request.POST.get('id')).update(
                    playbook_name=request.POST.get('playbook_name'),
                    playbook_desc=request.POST.get('playbook_desc'),
                    playbook_path=request.POST.get('playbook_path'),
                    playbook_file_name=request.POST.get('playbook_file_name'),
                    playbook_type=request.POST.get('playbook_type'),
                )
                return JsonResponse({'msg': "操作成功", "code": 0, 'data': []})
            except Exception, e:
                return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})
        elif mode == 'delete':
            try:
                print request.POST.get('id')
                TF_Playbook_Config.objects.filter(id=request.POST.get('id')).delete()
                return JsonResponse({'msg': "操作成功", "code": 0, 'data': []})
            except Exception, e:
                print e
                return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})
        elif mode == 'byId':
            try:
                snippet = TF_Playbook_Config.objects.get(id=request.POST.get('id'))
                data = {
                    'id': snippet.id,
                    'playbook_name': snippet.playbook_name,
                    'playbook_desc': snippet.playbook_desc,
                    'playbook_path': snippet.playbook_path,
                    'playbook_file_name': snippet.playbook_file_name,
                    'playbook_type': snippet.playbook_type,
                    'update_time': snippet.update_time
                }
                return JsonResponse({'msg': "操作成功", "code": 0, 'data': data})
            except Exception, e:
                print e
                return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})

        elif mode == 'select':
            try:
                iDisplayStart = request.POST.get('iDisplayStart', 0)
                iDisplayLength = request.POST.get('iDisplayLength', 10)
                page = request.POST.get('page')
                obj = TF_Playbook_Config.objects.all()  # 之前需要从models中导入device

                if len(request.POST.get('playbook_type')) > 0:
                    obj = obj.filter(playbook_type=request.POST.get('playbook_type'))

                if len(request.POST.get('playbook_name')) > 0:
                    obj = obj.filter(playbook_name__contains=request.POST.get('playbook_name'))

                if len(request.POST.get('playbook_file_name')) > 0:
                    obj = obj.filter(playbook_file_name__contains=request.POST.get('playbook_file_name'))

                total = obj.count();

                paginator = Paginator(obj, iDisplayLength)  # 设置device在每页显示的数量
                list = paginator.page(page)  # 取页数据
                rest = {
                    "iTotalRecords": int(iDisplayStart),  # 本次加载记录数量
                    "iTotalDisplayRecords": total,  # 总记录数量
                    # "sEcho" : sEcho,
                    "aaData": []}
                data = []

                for item in list:
                    res = {
                        'id': item.id,
                        'playbook_name': item.playbook_name,
                        'playbook_desc': item.playbook_desc,
                        'playbook_path': item.playbook_path,
                        'playbook_file_name': item.playbook_file_name,
                        'playbook_type': item.playbook_type,
                        'update_time': item.update_time
                    }
                    data.append(res)
                rest['aaData'] = data
                return JsonResponse(rest)
            except Exception, e:
                print '============== ======error'
                print e
                return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})
        # 'editPlaybook'
        elif mode == 'editPlaybook':
            try:
                id_ = request.POST.get('id')

                to_be_edited = TF_Playbook_Config.objects.get(id=id_)
                file_name = to_be_edited.playbook_name
                type_ = to_be_edited.playbook_type
                location = os.path.join(to_be_edited.playbook_path,
                                        to_be_edited.playbook_file_name)
                with open(location, 'r') as playbook:
                    content = playbook.read()
                data = {'playbook_id': id_, 'playbook_content': content}
                print('sending playbook', content)
                return JsonResponse({'msg': "操作成功", "code": 0, 'data': data})
            except Exception, e:
                return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})
        # end of editing playbook
        elif mode == 'updatePlaybook':
            try:
                id_ = request.POST.get('id')
                content = request.POST.get('playbook_content')

                to_be_updated = TF_Playbook_Config.objects.get(id=id_)
                location = os.path.join(to_be_updated.playbook_path,
                                        to_be_updated.playbook_file_name)
                print('update', location, 'with', content)
                with open(location, 'w') as playbook:
                    playbook.write(content)
                return JsonResponse({'msg': "操作成功", "code": 0, 'data': []})
            except Exception, e:
                return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})
        elif mode == 'validatePlaybook':
            KEYWORDS_IN_ANSIBLE_PLAYBOOK_CHECK = ['[WARNING]', 'ERROR', ]
            try:
                content = request.POST.get('playbook_content')
                temp_file = tempfile.NamedTemporaryFile(delete=True)
                location = temp_file.name
                KEYWORDS_IN_ANSIBLE_PLAYBOOK_CHECK.append(location)
                with open(location, 'w') as temp:
                    temp.write(content)
                validation_result = subprocess.check_output(['ansible-playbook', '-C', location],
                                                            stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError, e:
                validation_result = e.output
            try:  # construct returning msg.
                msg = [line for line in validation_result.split('\n')]
                # msg = [line for line in validation_result.split('\n')
                # for keyword in KEYWORDS_IN_ANSIBLE_PLAYBOOK_CHECK
                # if keyword in line]
            except Exception, e:
                print(e)
                return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})
            return JsonResponse({'msg': "操作成功", "code": 0,
                                 'data': {'msg': '\n'.join(msg)}})
        elif mode == 'editRoles':
            try:
                id_ = request.POST.get('id')

                to_be_edited = TF_Playbook_Config.objects.get(id=id_)
                file_name = to_be_edited.playbook_name
                location = os.path.join(to_be_edited.playbook_path,
                                        to_be_edited.playbook_file_name)
                with open(location, 'r') as playbook:
                    content = yaml.load(playbook)
                # Playbook yaml is a python list after serialization
                get_roles = operator.getitem
                roles_field = get_roles(content, 0).get('roles', None)
                used_roles = set()
                if roles_field:
                    for role in roles_field:
                        if isinstance(role, str):
                            used_roles.add(role)
                        elif isinstance(role, dict):
                            used_roles.add(role.get('role'))

                    used_roles = filter(lambda x: x is not None, used_roles)

                    # Find out the missing roles.
                    path_with_root = functools.partial(os.path.join,
                                                       project_settings.ROLE_TREE_ROOT)
                    missing_roles = filter(lambda path: not os.path.isdir(path),
                                           map(path_with_root, used_roles))
                    if missing_roles:
                        missing_roles_without_root = [os.path.split(role)[1]
                                                      for role in missing_roles]
                        available_roles = set(used_roles) - set(missing_roles_without_root)
                        return JsonResponse({'msg': "操作成功", "code": -2,
                                             'error': '缺少以下roles:\n' + ';\n'.join(missing_roles_without_root),
                                             'data': [role for role in available_roles]})
                    return JsonResponse({'msg': "操作成功", "code": 0,
                                         'data': ';'.join(used_roles)})
                else:
                    return JsonResponse({'msg': "操作失败", "code": -1,
                                         'error': 'There is no `roles` in this playbook.'})
            except Exception, e:
                print('Bugs happened.', location, e)
                return JsonResponse({'msg': "操作失败", "code": -1, 'error':
                    'Unkonwn error 233'})
        else:
            return render_to_response('inventory/inventory_list_yaml.html', {"user": request.user,
                                                                             "errorInfo": "mode illegal "},
                                      context_instance=RequestContext(request))


@login_required()
@permission_required('OpsManage.can_read_tf_device_info', login_url='/noperm/')
def upload(request):
    if request.method == "POST":
        try:
            file_obj = request.FILES.get('file')
            if file_obj:  # 处理附件上传到方法
                request_set = {}
                filename = os.path.join("/data/upload", file_obj.name)
                fobj = open(filename, 'wb');
                for chrunk in file_obj.chunks():
                    fobj.write(chrunk);
                fobj.close()
                recv_size = 0
                return JsonResponse({'msg': "操作成功", "code": 0})
            else:
                return JsonResponse({'msg': "未选择上传文件", "code": -100})
        except Exception, e:
            print e
            return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})
