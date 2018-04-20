#!/usr/bin/env python  
# _#_ coding:utf-8 _*_
import json
from django.http import JsonResponse
from django.shortcuts import render
from djcelery.models import PeriodicTask, CrontabSchedule, WorkerState, TaskState, IntervalSchedule
from django.contrib.auth.decorators import login_required
from celery import task
from celery.registry import tasks as cTasks
from celery import registry
from celery.five import keys, items
from django.contrib.auth.decorators import permission_required
from OpsManage.models import Ansible_Playbook


@login_required()
@permission_required('djcelery.change_periodictask', login_url='/noperm/')
def task_dispatch(request):
    if request.method == "GET":
        # 获取注册的任务
        regTaskList = []
        for task in list(keys(cTasks)):
            if task.startswith('OpsManage.tasks.ansible') or task.startswith('OpsManage.tasks.sched'):
                regTaskList.append(task)
        try:
            crontabList = CrontabSchedule.objects.all().order_by("-id")
            intervalList = IntervalSchedule.objects.all().order_by("-id")
            taskList = PeriodicTask.objects.all().order_by("-id")
            playbookList = Ansible_Playbook.objects.all()
        except:
            crontabList = []
            intervalList = []
            taskList = []
        return render(request, 'crontask/task_dispatch.html', {"user": request.user, "crontabList": crontabList,
                                                               "intervalList": intervalList, "taskList": taskList,
                                                               "regTaskList": regTaskList,
                                                               "playbookList": playbookList})


@login_required()
@permission_required('djcelery.change_periodictask', login_url='/noperm/')
def addCrontab(request):
    if request.method == "POST":
        try:
            CrontabSchedule.objects.create(minute=request.POST.get('minute'), hour=request.POST.get('hour'),
                                           day_of_week=request.POST.get('day_of_week'),
                                           day_of_month=request.POST.get('day_of_month'),
                                           month_of_year=request.POST.get('month_of_year'),
                                           )
            return JsonResponse({"code": 200, "data": None, "msg": "添加成功"})
        except:
            return JsonResponse({"code": 500, "data": None, "msg": "添加失败"})


@login_required()
@permission_required('djcelery.change_periodictask', login_url='/noperm/')
def delCrontab(request):
    if request.method == "POST":
        try:
            CrontabSchedule.objects.get(id=request.POST.get('id')).delete()
            return JsonResponse({"code": 200, "data": None, "msg": "删除成功"})
        except:
            return JsonResponse({"code": 500, "data": None, "msg": "删除失败"})


@login_required()
@permission_required('djcelery.change_periodictask', login_url='/noperm/')
def addInterval(request):
    if request.method == "POST":
        try:
            IntervalSchedule.objects.create(every=request.POST.get('every'), period=request.POST.get('period'))
            return JsonResponse({"code": 200, "data": None, "msg": "添加成功"})
        except:
            return JsonResponse({"code": 500, "data": None, "msg": "添加失败"})


@login_required()
@permission_required('djcelery.change_periodictask', login_url='/noperm/')
def delInterval(request):
    if request.method == "POST":
        try:
            IntervalSchedule.objects.get(id=request.POST.get('id')).delete()
            return JsonResponse({"code": 200, "data": None, "msg": "删除成功"})
        except:
            return JsonResponse({"code": 500, "data": None, "msg": "删除失败"})
    else:
        return JsonResponse({"code": 500, "data": None, "msg": "不支持的操作或者您没有权限操作操作此项。"})


@login_required()
@permission_required('djcelery.change_periodictask', login_url='/noperm/')
def task_model(request):
    if request.method == "GET":
        # 获取注册的任务
        regTaskList = []
        for task in list(keys(cTasks)):
            if task.startswith('OpsManage.tasks.ansible') or task.startswith('OpsManage.tasks.sched'):
                regTaskList.append(task)
        try:
            crontabList = CrontabSchedule.objects.all().order_by("-id")
            intervalList = IntervalSchedule.objects.all().order_by("-id")
            taskList = PeriodicTask.objects.all().order_by("-id")
            playbookList = Ansible_Playbook.objects.all()

            newtaskList = []
            for item in taskList:
                if item.kwargs.find('playbook_id') == -1:
                    continue
                kwargs = json.loads(item.kwargs)
                playbook_id = kwargs["playbook_id"]
                playbook = Ansible_Playbook.objects.get(id=int(playbook_id))
                task = {'id': item.id,
                        'name': item.name,
                        'task': item.task,
                        'last_run_at': item.last_run_at,
                        'total_run_count': item.total_run_count,
                        'enabled': item.enabled,
                        'crontab_id': item.crontab_id,
                        'interval_id': item.interval_id,
                        'expires': item.expires,
                        'playbook_name': playbook.playbook_name,
                        }
                newtaskList.append(task)
        except:
            crontabList = []
            intervalList = []
            newtaskList = []
        return render(request, 'crontask/task_model.html', {"user": request.user, "crontabList": crontabList,
                                                            "intervalList": intervalList, "taskList": newtaskList,
                                                            "regTaskList": regTaskList, "playbookList": playbookList})


@login_required()
@permission_required('djcelery.change_periodictask', login_url='/noperm/')
def addTask(request):
    if request.method == "POST":
        try:
            kwargs_data = {
                "playbook_id": int(request.POST.get('task')),
                "cron_task_name": request.POST.get('name')
            }
            PeriodicTask.objects.create(name=request.POST.get('name'),
                                        interval_id=request.POST.get('interval', None),
                                        # task=request.POST.get('task',None),
                                        task='crontask.views.ansible_celery_task.AnsiblePlayBook',
                                        crontab_id=request.POST.get('crontab', None),
                                        args=request.POST.get('args', '[]'),
                                        # kwargs = request.POST.get('kwargs','{}'),
                                        kwargs=json.dumps(kwargs_data),
                                        queue=request.POST.get('queue', 'ansible'),
                                        enabled=int(request.POST.get('enabled', 1)),
                                        expires=request.POST.get('expires', None)
                                        )
            return JsonResponse({"code": 200, "data": None, "msg": "添加成功"})
        except Exception, e:
            return JsonResponse({"code": 500, "data": str(e), "msg": "添加失败"})


@login_required()
@permission_required('djcelery.change_periodictask', login_url='/noperm/')
def delTask(request):
    if request.method == "POST":
        try:
            PeriodicTask.objects.get(id=request.POST.get('id')).delete()
            return JsonResponse({"code": 200, "data": None, "msg": "删除成功"})
        except:
            return JsonResponse({"code": 500, "data": None, "msg": "删除失败"})

@login_required()
@permission_required('djcelery.change_periodictask', login_url='/noperm/')
def editTask(request):
    if request.method == "POST":
        try:
            task = PeriodicTask.objects.get(id=request.POST.get('id'))
            task.name = request.POST.get('name')
            task.interval_id = request.POST.get('interval', None)
            task.crontab_id = request.POST.get('crontab', None)
            # task.args = request.POST.get('args')
            # task.kwargs = request.POST.get('kwargs')
            # task.queue = request.POST.get('queue',None)
            task.expires = request.POST.get('expires', None)
            task.enabled = int(request.POST.get('enabled'))
            task.save()
            return JsonResponse({"code": 200, "data": None, "msg": "修改成功"})
        except Exception, e:
            return JsonResponse({"code": 500, "data": str(e), "msg": "修改失败"})
    else:
        return JsonResponse({"code": 500, "data": None, "msg": "不支持的操作或者您没有权限操作操作此项。"})

