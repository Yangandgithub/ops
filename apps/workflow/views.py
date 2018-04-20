# -*- coding: utf-8 -*-
import json
import os

from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator

from OpsManage.models import TF_Workflow, TF_Playbook_Config

from OpsManage.data.DsMySQL import AnsibleRecord

from workflow.tasks import Workflow


def workflow(request):
    if request.method == "GET":
        workflows = TF_Workflow.objects.all()
        return render(request, 'workflow/workflow.html',
            {'user': request.user, 'workflow': workflow})

    if request.method == "POST":
        mode = request.POST.get('mode')
        if mode == "getNodes":  # return all the valid nodes for workflow
            nodes = TF_Playbook_Config.objects.all()
            print('Returning all the available nodes')
            result = []
            for node in nodes:
                task_id = node.id
                task_name = node.playbook_name
                n = {'taskId': task_id, 'name': task_name}
                result.append(n)
            return JsonResponse({'nodes': result})

        elif mode == 'select':  # Used to return all the pre-defined workflow
            try:
                iDisplayStart = request.POST.get('iDisplayStart', 0)
                iDisplayLength = request.POST.get('iDisplayLength', 10)
                page = request.POST.get('page')
                obj = TF_Workflow.objects.all()
                total = obj.count()
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
                        'workflow_name': item.workflow_name,
                        'workflow_desc': item.workflow_desc,
                        'workflow_path': item.workflow_path,
                        'workflow_filename': item.workflow_filename,
                    }
                    data.append(res)
                rest['aaData'] = data
                return JsonResponse(rest)
            except Exception, e:
                print e
                return JsonResponse({'msg': "操作失败", "code": -1, 'data': []})

        elif mode == 'createWorkflow':  # edit the specific workflow
            try:
                workflow_name = request.POST.get('workflow_name')
                workflow_desc = request.POST.get('workflow_desc')
                workflow_path = request.POST.get('workflow_path')
                workflow_filename = request.POST.get('workflow_filename')
                TF_Workflow.objects.create(
                    workflow_name=workflow_name,
                    workflow_desc=workflow_name,
                    workflow_path=workflow_path,
                    workflow_filename=workflow_filename,
                )
                location = os.path.join(workflow_path, workflow_filename)
                if not os.path.exists(location):
                    f = open(location, 'w')
                    f.close()
                AnsibleRecord.WorkflowOperationLog.insert(
                    workflow_name=workflow_name, content='创建Workflow',
                    oper_user=request.user)
                return JsonResponse({'msg': "操作成功", "code": 0, })
            except e:
                print e
                return JsonResponse({'msg': "操作失败", "code": -1, })

        elif mode =='alterWorkflow':
            # recieve the new workflow attribute
            try:
                workflow_id = int(request.POST.get('workflow_id'))
                to_be_altered = TF_Workflow.objects.filter(id=workflow_id)
                new_workflow_name = request.POST.get('workflow_name_alter')
                new_workflow_desc = request.POST.get('workflow_desc_alter')
                new_workflow_path = request.POST.get('workflow_path_alter')
                new_workflow_filename = request.POST.get('workflow_filename_alter')
                to_be_altered.update(workflow_name=new_workflow_name,
                                     workflow_desc=new_workflow_desc,
                                     workflow_path=new_workflow_path,
                                     workflow_filename=new_workflow_filename)
                AnsibleRecord.WorkflowOperationLog.insert(
                    workflow_name=workflow_name, content='修改Workflow',
                    oper_user=request.user)
            except Exception as e:
                return JsonResponse({'msg': "操作Failed", "code": -1, })
            else:
                return JsonResponse({'msg': "操作成功", "code": 0, })

        elif mode =='getWorkflowAttrs':
            # recieve the new workflow attribute
            workflow_id = request.POST.get('workflow_id')
            concrete_workflow = TF_Workflow.objects.get(id=workflow_id)
            try:
                concrete_workflow = TF_Workflow.objects.get(id=workflow_id)
                data = {}
                data['workflow_id'] = concrete_workflow.id
                data['workflow_name'] = concrete_workflow.workflow_name
                data['workflow_desc'] = concrete_workflow.workflow_desc
                data['workflow_path'] = concrete_workflow.workflow_path
                data['workflow_filename'] = concrete_workflow.workflow_filename
            except Exception as e:
                data = {}
                return JsonResponse({'msg': "操作Failed", "code": -1,
                                     'data': data})
            else:
                return JsonResponse({'msg': "操作成功", "code": 0,
                                     'data': data})

        elif mode =='deleteWorkflow':
            workflow_id = request.POST.get('workflow_id')
            wf = TF_Workflow.objects.get(id=workflow_id)
            location = os.path.join(wf.workflow_path, wf.workflow_filename)
            try:
                TF_Workflow.objects.filter(id=workflow_id).delete()
                AnsibleRecord.WorkflowOperationLog.insert(
                    workflow_name=workflow_name, content='删除Workflow',
                    oper_user=request.user)
                os.remove(location)
            except Exception as e:
                print(e)
                return JsonResponse({'msg': "操作成功", "code": 0, 'data': []})
            except OSError as e:
                print(e)
                return JsonResponse({'msg': "操作成功", "code": 0, 'data': []})

        elif mode == 'editWorkflow':  # edit the specific workflow
            workflow_id = request.POST.get('workflow_id') or None
            if workflow_id:
                try:
                    wf = TF_Workflow.objects.get(id=workflow_id)
                except TF_Workflow.DoesNotExist:
                    wf_location = os.path.join(settings.WORKFLOW_LOCATION, 'test')
                else:
                    wf_location = os.path.join(wf.workflow_path, wf.workflow_filename)
                try: 
                    with open(wf_location, 'r') as f:
                        data = json.load(f) or None
                except ValueError:  # there is nothing in the file
                    data = None
                return JsonResponse({'msg': "操作成功", "code": 0, 'data': data})

        elif mode == 'alterWorkflowDefinition':
            workflow_id = request.POST.get('workflow_id') or None
            workflow_definition = json.loads(request.POST.get('workflow'))
            workflow_definition['workflowId'] = int(workflow_id)
            print('recieved', type(workflow_definition))
            if workflow_id:
                try:
                    wf = TF_Workflow.objects.get(id=workflow_id)
                except TF_Workflow.DoesNotExist as e:
                    print(e)
                    wf_location = os.path.join(settings.WORKFLOW_LOCATION, 'test')
                else:
                    wf_location = os.path.join(wf.workflow_path,
                                               wf.workflow_filename)
                try: 
                    with open(wf_location, 'w') as f:
                        json.dump(workflow_definition, f)
                except ValueError as e:  # there is nothing in the file
                    print(e)
                    wf_location = os.path.join(settings.WORKFLOW_LOCATION, 'test')
                finally:
                    return JsonResponse({'msg': "操作成功", "code": 0})



def launch_workflow(request):
    '''Try to run an atmoic task. Support both normal and workflow.'''
    # TODO: to be reimplemented
    if request.method == 'POST':
        workflow_id = request.POST.get('workflow_id')
                             
        concrete_workflow = TF_Workflow.objects.get(id=workflow_id)

        workflow_file = os.path.join(concrete_workflow.workflow_path,
                                     concrete_workflow.workflow_filename)
        with open(workflow_file) as f:
            workflow = json.load(f)
        print 'Trying to execute Workflow {}'.format(workflow_file) 
        wat = Workflow(workflow)
        log_id = wat.execute(concrete_workflow.workflow_name, request.user)

        return JsonResponse({'msg': "OK", "code": 0, "taskId": log_id})
