#!/usr/bin/env python
# _#_ coding:utf-8 _*_
import uuid, os, json
import time
import datetime
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from OpsManage.serializers import *
from django.contrib.auth.models import User, Group
from OpsManage.models import Ansible_CallBack_PlayBook_Result
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from django.core.paginator import PageNotAnInteger, Paginator, InvalidPage, EmptyPage


@login_required()
def ansible_playbook_sum(request):
    if request.method == "POST":
        try:
            logId = Log_Ansible_Playbook.objects.get(id=request.POST.get('playbook_id'))
            resultData = []
            statPer = {
                "unreachable": 0,
                "skipped": 0,
                "changed": 0,
                "ok": 0,
                "failed": 0
            }
            for ds in Ansible_CallBack_PlayBook_Result.objects.filter(logId=logId).filter(Q(status=0) | Q(status=1)):
                if ds.content != "":
                    data = {
                        "unreachable": 0,
                        "skipped": 0,
                        "changed": 0,
                        "ok": 0,
                        "failed": 0,
                        "result": "Failed",
                        "host": " "
                    }
                    host = ds.content.split(":")[0]
                    ok = ds.content.split(":")[1].split()[0].split("=")[1]
                    failed = ds.content.split(":")[1].split()[4].split("=")[1]
                    changed = ds.content.split(":")[1].split()[1].split("=")[1]
                    skipped = ds.content.split(":")[1].split()[3].split("=")[1]
                    unreachable = ds.content.split(":")[1].split()[2].split("=")[1]
                    if ds.status == 0:
                        result = "Succeed"
                    else:
                        result = "Failed"

                    data['unreachable'] = unreachable
                    data['skipped'] = skipped
                    data['changed'] = changed
                    data['ok'] = ok
                    data['failed'] = failed
                    data['result'] = result
                    data['host'] = host
                    resultData.append(data)
                    statPer['unreachable'] = int(unreachable) + statPer['unreachable']
                    statPer['skipped'] = int(skipped) + statPer['skipped']
                    statPer['changed'] = int(changed) + statPer['changed']
                    statPer['failed'] = int(failed) + statPer['failed']
                    statPer['ok'] = int(ok) + statPer['ok']
        except Exception, e:
            return JsonResponse({'msg': "查看汇总结果失败", "code": 500, 'data': e})

        return JsonResponse({'msg': "操作成功", "code": 200, 'data': resultData, "statPer": statPer})


@login_required()
def ansible_modle_concise(request):
    if request.method == "POST":
        try:
            result = ''
            logId = Log_Ansible_Model.objects.get(id=request.POST.get('model_id'))

            for ds in Ansible_CallBack_Model_Result.objects.filter(logId=logId):
                if ds.result != 0:
                    content = "FAILED"
                else:
                    content = ds.content1

                result += ds.device_id + "|" + content
                result += '\n'

        except Exception, e:
            return JsonResponse({'msg': "查看失败", "code": 500, 'data': e})

        return JsonResponse({'msg': "操作成功", "code": 200, 'data': result})


@login_required()
def ansible_modle_export(request):
    if request.method == "POST":
        try:
            result = []
            logId = Log_Ansible_Model.objects.get(id=request.POST.get('model_id'))

            for ds in Ansible_CallBack_Model_Result.objects.filter(logId=logId):
                if ds.result != 0:
                    content = "FAILED"
                else:
                    content = ds.content1.replace("\n", " ").replace(",", " ")

                data = ds.device_id + "," + content
                result.append(data)

        except Exception, e:
            return JsonResponse({'msg': "查看失败", "code": 500, 'data': e})

        return JsonResponse({'msg': "操作成功", "code": 200, 'data': result})


@login_required(login_url='/login')
def list_ansible_log(request):
    if request.method == "GET":
        return render_to_response('ansible/ansible_log.html', {"user": request.user},
                                  context_instance=RequestContext(request))

@login_required(login_url='/login')
def ansible_model_log(request):
    if request.method == "GET":
        return render_to_response('ansible/ansible_log.html', {"user": request.user},
                                  context_instance=RequestContext(request))
    if request.method == "POST":
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


@login_required(login_url='/login')
def ansible_playbook_log(request):
    if request.method == "GET":
        return render_to_response('ansible/ansible_log.html', {"user": request.user},
                                  context_instance=RequestContext(request))
    if request.method == "POST":
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
def ansible_model_log_view(request):
    if request.method == "POST":
        try:
            result = ''
            logModelID = request.POST.get('logModelID')
            logId = Log_Ansible_Model.objects.get(id=logModelID)
            for ds in Ansible_CallBack_Model_Result.objects.filter(logId=logId):
                result += ds.content
                result += '\n'
        except Exception, e:
            return JsonResponse({'msg': "查看失败", "code": 500, 'data': e})


@login_required(login_url='/login')
def ansible_playbook_log_view(request):
    if request.method == "POST":
        try:
            result = ''
            logPlaybookID = request.POST.get('logPlaybookID')
            logId = Log_Ansible_Playbook.objects.get(id=logPlaybookID)
            for ds in Ansible_CallBack_PlayBook_Result.objects.filter(logId=logId):
                result += ds.content
                result += '\n'
        except Exception, e:
            return JsonResponse({'msg': "查看失败", "code": 500, 'data': e})
    return JsonResponse({'msg': "操作成功", "code": 200, 'data': result})
