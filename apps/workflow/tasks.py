# -*- coding: utf-8 -*-
"""
This is a beta implementation, current circumstances include:
    1) Two kinds of task unit, one is normal atomic task which just a Ansible
    Playbook and its relevant stuffs while the other is workflow in which
    defines the executing sequence based on a normal atomic task's result and
    its onSuccess, onFailure and onAlways edges pointing to another atomic
    task. Both ends of an edges can be the exact same one atomic task.
    2) The atomic task stored in the DB only contains its name, sub-type(see
    below), path on the file system and then noting important.
    Example diagram of workflow task:

            -----------------                 -----------------
            | Atomic Task 1 |                 | Atomic Task 4 |
    (START) -----------------                 -----------------
            |  extra_vars:  | ---(onAlways)-->|  extra_vars:  |
            | { hosts: web1,|                 | { hosts: cdh, |
            |   port: 22, } |                 |   user: ??, } |
            -----------------                 -----------------
            /             \                        \
      (onSuccess)     (onFailure)              (onFailure)
          /                 \                        \
    -----------------    -----------------    -----------------
    | Atomic Task 2 |    | Atomic Task 3 |    | Atomic Task 3 |
    -----------------    -----------------    -----------------
    |  extra_vars:  |    |  extra_vars:  |    |  extra_vars:  |
    | { hosts: web2,|    | { hosts: db2, |    | { hosts: test,|
    |   port: 22, } |    |  port: 22, }  |    |   port: 22, } |
    -----------------    -----------------    -----------------
"""

__all__ = ['WorkflowTaskExecutor']
__version__ = 'beta'


import os
import json
import time

import django
# 自动判断版本
if django.VERSION >= (1, 7):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OpsManage.settings")
    django.setup()


from django.conf import settings
from celery import Celery
from ansible.plugins.callback import CallbackBase

from OpsManage.utils.ansible_api_v2 import ANSRunner
from OpsManage.data.DsMySQL import AnsibleRecord
from OpsManage.data.DsRedisOps import DsRedis
from OpsManage.models import TF_Playbook_Config


workflow_app = Celery('workflow_task', broker='redis://172.17.0.4:6379/1',
                      backend='redis://172.17.0.4:6379/2')


class AtomicTaskDoesNotExist(Exception):
    """AtomicTask defined in workflow does not exist."""
    pass


class AtomicTaskFilenameDoesNotMatch(Exception):
    """AtomicTask's name does not match with the one in database."""
    pass


class AtomicTask(object):

    __slots__ = ['task_file', 'extra_vars', 'resource',
                 '_on_success', '_on_failure', '_on_always',
                 'redisKey', 'logId',]

    def __init__(self, task_file, extra_vars=None,
                 on_success=None, on_failure=None, on_always=None,
                 redisKey=None, logId=None):
        """Initialize the normal atomic task.

        :param task_file: Filesystem location of Ansible playbook.
        :param extra_vars: A dict contains vars at least have 'hosts' part.
        :param on_success: Next NAT to execute while this one succeed.
        :param on_failure: Next NAT to execute while this one fail.
        :param on_always: Next NAT to execute ignore the executing result.
        :param redis_key: A str var used in logging, follow the original api.
        :param log_id: A str var used in logging, follow the original api.
        """
        assert os.path.isfile(task_file)
        self.task_file = task_file
        if extra_vars is None:
            self.extra_vars = {}
        else:
            self.extra_vars = extra_vars
        self._on_success = on_success
        self._on_failure = on_failure
        self._on_always = on_always
        self.resource = self.extra_vars.get('myhosts') or str(settings.DEFAULT_INVENTORY)

        self.redisKey = redisKey
        self.logId = logId

    @property
    def on_success(self):
        return self._on_success

    @on_success.setter
    def on_success(self, nat):
        assert isinstance(nat, AtomicTask), 'on_success should be a atomic task'
        self._on_success = nat

    @property
    def on_failure(self):
        return self._on_failure

    @on_failure.setter
    def on_failure(self, nat):
        assert isinstance(nat, AtomicTask), 'on_failure should be a atomic task'
        self._on_failure = nat

    @property
    def on_always(self):
        return self._on_always

    @on_always.setter
    def on_always(self, nat):
        assert isinstance(nat, AtomicTask), 'on_always should be a atomic task'
        self._on_always = nat

    def __repr__(self):
        return ('AtomicTask object {:x} with task_file: {} '
                'extra_vars: {}').format(id(self), self.task_file,
                                         self.extra_vars)


class Workflow:
    test_wf = {
	"edgeList": [
	    {
		"destination": "PING-LOCALHOST",
		"source": "START",
		"status": "always"
	    },
	    {
		"destination": "PING-UNREACHABLE",
		"source": "PING-LOCALHOST",
		"status": "error"
	    },
	    {
		"destination": "PING-LOCALDOMAIN",
		"source": "PING-LOCALHOST",
		"status": "success"
	    },
	    {
		"destination": "PING-LOCALHOST2",
		"source": "PING-LOCALDOMAIN",
		"status": "error"
	    }
	],
	"widgetList": [
	    {
		"id": "START",
		"taskId": -1,
		"name": "start",
		"parameter": {},
	    },
	    {
		"id": "PING-LOCALHOST",
		"taskId": 28,
		"name": "ping localhost",
		"parameter": {},
	    },
	    {
		"id": "PING-LOCALDOMAIN",
		    "taskId": 48,
		"name": "ping localdoamin",
		"parameter": {
			'hosts': os.path.join(os.path.dirname(__file__),
                        'inventory_for_test_workflow')
		}
	    },
	    {
		"id": "PING-UNREACHABLE",
		"taskId": 47,  # when start node fail
		"name": "ping unreachable",
		"parameter": {},
	    },
	    {
		"id": "PING-LOCALHOST2",
		"taskId": 28,  # when ping localdomain fail
		"name": "ping localhost when ping localdomain fail",
		"parameter": {'why': 'when localdomain fail'}
	    }
	]
    }
    __slots__ = ('_workflow, _nats, _results')

    def __init__(self, workflow=None):
        """Workflow from a tree-like definition file.
    
        :param workflow_file: Filesystem location of workflow definition file.
        """
        if workflow is None:
            self._workflow = self.__class__.test_wf
        else:
            self._workflow = workflow
        self._nats = {}
        self._create_atomic_tasks()  # heavy logic in here
    
    def _create_atomic_tasks(self):
        """Recursively create NAT objects and set up their on_xxx callback."""
        nodes = self._workflow.get('widgetList')
        for node in nodes:
            node_id = node.get('id')  # the random node id of NAT used by frontend
            id_ = node.get('taskId')  # the id of Atomic Task in DB
            if id_ is None or id_ is u'':  # the meaningless `START` node
                self._id_of_start = node_id
                continue
            param = node.get('parameter')
            if param is None or param is u'':
                extra_vars = {}
            else:
                extra_vars = json.loads(param)
            name = node.get('name')
            try:
                config = TF_Playbook_Config.objects.get(id=id_)
            except TF_Playbook_Config.DoesNotExist:
                raise AtomicTaskDoesNotExist()
            except AssertionError:
                raise AtomicTaskFilenameDoesNotMatch()
            task_file = os.path.join(config.playbook_path,
                                     config.playbook_file_name)
            nat = AtomicTask(task_file=str(task_file), extra_vars=extra_vars)
            self._nats[node_id] = nat

        edges = self._workflow.get('edgeList')

        # set up relationship between nats aka the on_something attributes
        for edge in edges:
            # the ramdom string is the node id used by front end.
            # {
                # "destination": "CihfFDzfsepPzTx",
                # "source": "4D72hSPwPfJc4tY",
                # "status": "error"
            # }
            source = edge.get('source')
            if source == self._id_of_start:
                continue
            destination = edge.get('destination')
            on_something = self._format_naming(edge.get('status'))

            from_nat = self._nats.get(source)
            if from_nat:
                to_nat = self._nats.get(destination)
                setattr(from_nat, on_something, to_nat)

    def execute(self, workflow_name, oper_user):
        """Run the WAT with provided extra variables."""
        initialized_edge = filter(lambda d: d['source'] == self._id_of_start,
                                  self._workflow.get('edgeList'))[0]
        first_nat = self._nats[initialized_edge.get('destination')]
        log_id = AnsibleRecord.WorkflowOperationLog.insert(
            workflow_name=workflow_name, content='执行工作流',
            oper_user=oper_user)
        for node in self._nats.itervalues():
            setattr(node, 'logId', log_id)
        execute.delay(workflow=self, atomic_task=first_nat)
        #execute(workflow=self, atomic_task=first_nat)
        return log_id

    @staticmethod
    def _format_naming(arg):
        if arg == 'error':
            return 'on_failure'
        if arg == 'always':
            return 'on_always'
        if arg == 'success':
            return 'on_success'


@workflow_app.task
def execute(workflow, atomic_task):
    """Encapsulate the Ansible api, actually run a playbook"""
    runner = ANSRunner(resource=atomic_task.resource,
                       redisKey=atomic_task.redisKey, logId=atomic_task.logId)
    runner.run_playbook(host_list=None, playbook_path=atomic_task.task_file,
                        extra_vars=atomic_task.extra_vars)
    result = runner.get_playbook_result()
    print('*' * 32 + 'Result of {}'.format(atomic_task) + '*' * 32)
    print(result)
    print('*' * 32 + 'End of result.' + '*' * 32)
    
    # 添加 执行结果，前端可访问
    redisKey = 'WorkflowTask-{}-{}'.format(atomic_task.logId,
        atomic_task.task_file)
    DsRedis.OpsAnsiblePlayBook.lpush(redisKey, 'Done')

    if any((result['failed'], result['unreachable'])):  # on failure
        if atomic_task.on_failure is not None:
            node = atomic_task.on_failure
            print(('Executing {} encounter failure try to execute '
                   '{}').format(atomic_task, node))
            execute.delay(workflow, node)
    else:  # on success
        if atomic_task.on_success is not None:
            node = atomic_task.on_success
            print(('Executing {} encounter success try to execute '
                   '{}').format(atomic_task, node))
            execute.delay(workflow, node)
