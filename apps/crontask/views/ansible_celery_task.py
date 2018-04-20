#!/usr/bin/env python  
# _#_ coding:utf-8 _*_ 
import os,json
from celery import task
from OpsManage.models import (Ansible_Playbook,
                              Ansible_Playbook_Number,TF_Device_Info)
from OpsManage.data.DsMySQL import AnsibleRecord
from OpsManage.utils.ansible_api_v2 import ANSRunner
from django.conf import settings
    
@task  
def AnsiblePlayBook(**kw):
    logId = None
    sList = []
    resource = []
    try:
        if kw.has_key('playbook_id'):
            playbook = Ansible_Playbook.objects.get(id=kw.get('playbook_id'))
            filePath = settings.PLAYBOOK_PATH + '/' + str(playbook.playbook_file)
            try:
                numberList = Ansible_Playbook_Number.objects.filter(playbook=playbook)
                serverList = [s.playbook_server for s in numberList]
                for server in serverList:
                    server_assets = TF_Device_Info.objects.filter(device_id=server)
                    for iter in server_assets:
                        sList.append(iter.device_id)
                        resource.append({"hostname": iter.device_id, "ip": iter.ansible_ssh_host,
                                         "port": int(iter.ansible_ssh_port),
                                         "username": iter.ansible_ssh_user})
                playbook_vars = playbook.playbook_vars
                if len(playbook_vars) == 0:
                    playbook_vars = dict()
                else:
                    playbook_vars = json.loads(playbook_vars)
                playbook_vars['host'] = sList
            except Exception, ex:
                return ex

            logId = AnsibleRecord.PlayBook.insert(user='celery',ans_id=playbook.id,ans_name=kw.get('cron_task_name'),
                                            ans_content=u"执行定时任务",ans_server=','.join(sList))
            ANS = ANSRunner(resource,redisKey=None,logId=logId)
            ANS.run_playbook(host_list=sList, playbook_path=filePath, extra_vars=playbook_vars)
            return ANS.get_playbook_result()
    except Exception,e:
        return False       
    
