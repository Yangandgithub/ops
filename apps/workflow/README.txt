新代码框架、旧模型下WorkflowDemo
copy后无法直接运行，参考以下修改

Step1.(路由处理)
	在OpsManage/urls.py 中添加路由:
		url(r'^workflow/', include('workflow.urls', namespace='workflow')),
	Opsmanage/settings中添加app: 'workflow'
	修改OpsManage/templates/index.html 修改工作流对应的路由:
	 /workflow/workflow_task/

Step3.(日志记录相关)
	在 OpsManage/modesl.py 中追加所需模型

	class TF_Workflow(models.Model):
    	'''以文件形式存于文件系统的workflow'''
    	workflow_name = models.CharField(max_length=128, verbose_name='Workflow名称')
    	workflow_desc = models.CharField(max_length=512, verbose_name='Workflow描述',
                                    	 blank=True, null=True)
    	workflow_path = models.CharField(max_length=128, verbose_name='Workflow路径')
    	workflow_filename = models.CharField(max_length=128,
                                         	 verbose_name='Workflow文件名')
    	class Meta:
        	db_table = 'tf_workflow'
        	verbose_name = 'Workflow表'

	class IctWorkflowOperationLog(models.Model):
    	"""Try not to violate the new table schema"""
    	workflow_name = models.CharField(max_length=100,
                                     	verbose_name='Workflow任务名')
    	content = models.CharField(max_length=512, verbose_name='操作内容',
                               	   null=True)
    	oper_user = models.CharField(max_length=32, verbose_name='用户')
    	create_time = models.DateTimeField(auto_now_add=True,
                                       	   verbose_name='创建时间')
    	class Meta:
        	db_table = 'ict_workflow_operation_log'

	
	```
		python manage.py makemigrations OpsMange
		python manage.py migrate OpsManage
	```
	在 OpsManage/data/DsMysql.py 中添加相应接口，
	如果Playbook运行结果需要记录于新库中，新建模型 并修改 OpsManage/utils/ansible_api_v2 中
	PlayBookResultsCollectorToSaveDB 日志、结果记录方法


Step 3.(Workflow执行相关)
	修改 api中 MyInventory 的 __init__方法为:
        self.resource = resource
		# 使用文件系统中的Inventory
        if isinstance(self.resource, str) and os.path.exists(self.resource):
            print('Using file <{}> as inventory'.format(self.resource))
            self.inventory = Inventory(loader=loader,
                                       variable_manager=variable_manager,
                                       host_list=self.resource)
        else:
            self.inventory = Inventory(loader=loader,
                                       variable_manager=variable_manager,
                                       host_list=[])
        self.dynamic_inventory()

Step 4. (使用Workflow)
	Δ 因需求不确定，故作以下约定以便使用:
	1. 在编辑Workflow结点时， 添加额外参数为合法的JSON字符串;
	   主机信息、playbook参数都通过在输入框中填写JSON指定 
	  	Q.怎样指定该结点需要操作的主机?
	  	A.三种形式
		  ㈠ 单一主机 
			{
   				"myhosts":[
      				{
         				"hostname":"192.168.x.x",
         				"port":"22"
      				}
   				]
			}
		  ㈡ 多主机
		  	{
   				"myhosts":{
      				"group1":{
         				"hosts":[
            				{
               					"hostname":"xxx",
               					"port":"22"
            				},
            				{
               					"hostname2":"192.168.x.xx",
               					"port":22
            				}
         				]
      				},
      				"vars":{
         				"v1":"k1",
         				"v2":"k2"
      				}
   				}
			}
		  ㈢ 默认Inventory:
		     不填写 myhosts字段 在 OpsManage/settings中 添加默认地址
			 DEFAULT_INVENTORY = '/path/to'
	2. 目前Workflow执行逻辑为
	   先执行Workflow中第一个结点(原子任务，Playbook), 执行对象为
	   "myhosts"字段或默认Inventory； 获取该结点执行结果，若结果中
	   有"failed", "unreachable"则定义为失败，选择其定义的失败结点执行
	   若没有与执行结果一致的下一跳结点则Workflow结束
	3. 具体执行单元
	   后台接受到执行请求时，通过异步任务队列执行。需要先启动Workflow worker
	   Celery3.1 默认使用prefork的daemon进程执行任务，需要先
	   ```bash
	   		export PYTHONOPTIMIZE=1
	   		celery -A workflow.tasks worker -l info
	   ```
