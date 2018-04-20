#!/usr/bin/env python  
# _#_ coding:utf-8 _*_  
from django.db import models
import sys

reload(sys)
sys.setdefaultencoding("utf-8")


class Assets(models.Model):
    assets_type_choices = (
        ('server', u'服务器'),
        ('switch', u'交换机'),
        ('route', u'路由器'),
        ('printer', u'打印机'),
        ('scanner', u'扫描仪'),
        ('firewall', u'防火墙'),
        ('storage', u'存储设备'),
        ('wifi', u'无线设备'),
    )
    assets_type = models.CharField(choices=assets_type_choices, max_length=100, default='server', verbose_name='资产类型')
    name = models.CharField(max_length=100, verbose_name='资产编号', unique=True)
    sn = models.CharField(max_length=100, verbose_name='设备序列号')
    # blank：是否为空，相对于验证来说
    buy_time = models.DateField(blank=True, null=True, verbose_name='购买时间')
    expire_date = models.DateField(u'过保修期', null=True, blank=True)
    buy_user = models.CharField(max_length=100, blank=True, null=True, verbose_name='购买人')
    management_ip = models.GenericIPAddressField(u'管理IP', blank=True, null=True)
    manufacturer = models.CharField(max_length=100, blank=True, null=True, verbose_name='制造商')
    provider = models.CharField(max_length=100, blank=True, null=True, verbose_name='供货商')
    model = models.CharField(max_length=100, blank=True, null=True, verbose_name='资产型号')
    status = models.SmallIntegerField(blank=True, null=True, verbose_name='状态')
    put_zone = models.SmallIntegerField(blank=True, null=True, verbose_name='放置区域')
    group = models.SmallIntegerField(blank=True, null=True, verbose_name='使用组')
    business = models.SmallIntegerField(blank=True, null=True, verbose_name='业务类型')
    zone = models.ForeignKey('Zone_Assets', null=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'opsmanage_assets'
        permissions = (
            ("can_read_assets", "读取资产权限"),
            ("can_change_assets", "更改资产权限"),
            ("can_add_assets", "添加资产权限"),
            ("can_delete_assets", "删除资产权限"),
        )
        verbose_name = '总资产表'
        # 复数名称
        verbose_name_plural = '总资产表'


class Server_Assets(models.Model):
    assets = models.OneToOneField('Assets')
    ip = models.GenericIPAddressField(max_length=100, unique=True, blank=True, null=True, verbose_name='ip地址')
    hostname = models.CharField(max_length=100, blank=True, null=True, verbose_name='域名')
    username = models.CharField(max_length=100, blank=True, null=True, verbose_name='用户名')
    passwd = models.CharField(max_length=100, blank=True, null=True, verbose_name='密码')
    keyfile = models.SmallIntegerField(blank=True, null=True)
    # DecimalField，是一个固定精度的十进制数，必须有参数max_digits(最大精度)，decimal_places(起始)
    port = models.DecimalField(max_digits=6, decimal_places=0, blank=True, null=True, verbose_name='端口号')
    line = models.SmallIntegerField(blank=True, null=True)
    cpu = models.CharField(max_length=100, blank=True, null=True)
    cpu_number = models.SmallIntegerField(blank=True, null=True)
    vcpu_number = models.SmallIntegerField(blank=True, null=True)
    cpu_core = models.SmallIntegerField(blank=True, null=True)
    disk_total = models.CharField(max_length=100, blank=True, null=True)
    ram_total = models.IntegerField(blank=True, null=True)
    kernel = models.CharField(max_length=100, blank=True, null=True)
    selinux = models.CharField(max_length=100, blank=True, null=True)
    swap = models.CharField(max_length=100, blank=True, null=True)
    raid = models.SmallIntegerField(blank=True, null=True)
    system = models.CharField(max_length=100, blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'opsmanage_server_assets'
        # 自定义添加只读权限-系统自带了add change delete三种权限
        permissions = (
            ("can_read_server_assets", "读取服务器资产权限"),
            ("can_change_server_assets", "更改服务器资产权限"),
            ("can_add_server_assets", "添加服务器资产权限"),
            ("can_delete_server_assets", "删除服务器资产权限"),
        )
        verbose_name = '服务器资产表'
        verbose_name_plural = '服务器资产表'


class Network_Assets(models.Model):
    assets = models.OneToOneField('Assets')
    bandwidth = models.CharField(max_length=100, blank=True, null=True, verbose_name='背板带宽')
    ip = models.CharField(max_length=100, blank=True, null=True, verbose_name='管理ip')
    port_number = models.SmallIntegerField(blank=True, null=True, verbose_name='端口个数')
    firmware = models.CharField(max_length=100, blank=True, null=True, verbose_name='固件版本')
    cpu = models.CharField(max_length=100, blank=True, null=True, verbose_name='cpu型号')
    stone = models.CharField(max_length=100, blank=True, null=True, verbose_name='内存大小')
    configure_detail = models.TextField(max_length=100, blank=True, null=True, verbose_name='配置说明')
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'opsmanage_network_assets'
        permissions = (
            ("can_read_network_assets", "读取网络资产权限"),
            ("can_change_network_assets", "更改网络资产权限"),
            ("can_add_network_assets", "添加网络资产权限"),
            ("can_delete_network_assets", "删除网络资产权限"),
        )
        verbose_name = '网络资产表'
        verbose_name_plural = '网络资产表'


class Disk_Assets(models.Model):
    assets = models.ForeignKey('Server_Assets')
    device_volume = models.CharField(max_length=100, blank=True, null=True, verbose_name='硬盘容量')
    device_status = models.CharField(max_length=100, blank=True, null=True, verbose_name='硬盘状态')
    device_model = models.CharField(max_length=100, blank=True, null=True, verbose_name='硬盘型号')
    device_brand = models.CharField(max_length=100, blank=True, null=True, verbose_name='硬盘生产商')
    device_serial = models.CharField(max_length=100, blank=True, null=True, verbose_name='硬盘序列号')
    device_slot = models.SmallIntegerField(blank=True, null=True, verbose_name='硬盘插槽')
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'opsmanage_disk_assets'
        permissions = (
            ("can_read_disk_assets", "读取磁盘资产权限"),
            ("can_change_disk_assets", "更改磁盘资产权限"),
            ("can_add_disk_assets", "添加磁盘资产权限"),
            ("can_delete_disk_assets", "删除磁盘资产权限"),
        )
        unique_together = (("assets", "device_slot"))
        verbose_name = '磁盘资产表'
        verbose_name_plural = '磁盘资产表'


class Ram_Assets(models.Model):
    assets = models.ForeignKey('Server_Assets')
    device_model = models.CharField(max_length=100, blank=True, null=True, verbose_name='内存型号')
    device_volume = models.CharField(max_length=100, blank=True, null=True, verbose_name='内存容量')
    device_brand = models.CharField(max_length=100, blank=True, null=True, verbose_name='内存生产商')
    device_slot = models.SmallIntegerField(blank=True, null=True, verbose_name='内存插槽')
    device_status = models.CharField(max_length=100, blank=True, null=True, verbose_name='内存状态')
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'opsmanage_ram_assets'
        permissions = (
            ("can_read_ram_assets", "读取内存资产权限"),
            ("can_change_ram_assets", "更改内存资产权限"),
            ("can_add_ram_assets", "添加内存资产权限"),
            ("can_delete_ram_assets", "删除内存资产权限"),
        )
        unique_together = (("assets", "device_slot"))
        verbose_name = '内存资产表'
        verbose_name_plural = '内存资产表'


class NetworkCard_Assets(models.Model):
    assets = models.ForeignKey('Server_Assets')
    macaddress = models.CharField(u'MAC', max_length=64, unique=True)
    ipaddress = models.GenericIPAddressField(u'IP', blank=True, null=True)
    device_model = models.CharField(max_length=100, blank=True, null=True, verbose_name='网卡型号')
    device_brand = models.CharField(max_length=100, blank=True, null=True, verbose_name='网卡生产商')
    device_status = models.CharField(max_length=100, blank=True, null=True, verbose_name='网卡状态')
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'opsmanage_networkcard_assets'
        permissions = (
            ("can_read_networkcard_assets", "读取网卡资产权限"),
            ("can_change_networkcard_assets", "更改网卡资产权限"),
            ("can_add_networkcard_assets", "添加网卡资产权限"),
            ("can_delete_networkcard_assets", "删除网卡资产权限"),
        )
        verbose_name = '网卡资产表'
        verbose_name_plural = '网卡资产表'


class Service_Assets(models.Model):
    '''业务分组表'''
    service_name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'opsmanage_service_assets'
        permissions = (
            ("can_read_service_assets", "读取业务资产权限"),
            ("can_change_service_assets", "更改业务资产权限"),
            ("can_add_service_assets", "添加业务资产权限"),
            ("can_delete_service_assets", "删除业务资产权限"),
        )
        verbose_name = '业务分组表'
        verbose_name_plural = '业务分组表'


class Zone_Assets(models.Model):
    zone_name = models.CharField(max_length=100, unique=True)
    '''自定义权限'''

    class Meta:
        db_table = 'opsmanage_zone_assets'
        permissions = (
            ("can_read_zone_assets", "读取机房资产权限"),
            ("can_change_zone_assets", "更改机房资产权限"),
            ("can_add_zone_assets", "添加机房资产权限"),
            ("can_delete_zone_assets", "删除机房资产权限"),
        )
        verbose_name = '机房资产表'
        verbose_name_plural = '机房资产表'


class Line_Assets(models.Model):
    line_name = models.CharField(max_length=100, unique=True)
    '''自定义权限'''

    class Meta:
        db_table = 'opsmanage_line_assets'
        permissions = (
            ("can_read_line_assets", "读取出口线路资产权限"),
            ("can_change_line_assetss", "更改出口线路资产权限"),
            ("can_add_line_assets", "添加出口线路资产权限"),
            ("can_delete_line_assets", "删除出口线路资产权限"),
        )
        verbose_name = '出口线路资产表'
        verbose_name_plural = '出口线路资产表'


class Raid_Assets(models.Model):
    raid_name = models.CharField(max_length=100, unique=True)
    '''自定义权限'''

    class Meta:
        db_table = 'opsmanage_raid_assets'
        permissions = (
            ("can_read_raid_assets", "读取Raid资产权限"),
            ("can_change_raid_assets", "更改Raid资产权限"),
            ("can_add_raid_assets", "添加Raid资产权限"),
            ("can_delete_raid_assets", "删除Raid资产权限"),
        )
        verbose_name = 'Raid资产表'
        verbose_name_plural = 'Raid资产表'


class Log_Assets(models.Model):
    assets_id = models.IntegerField(verbose_name='资产类型id', blank=True, null=True, default=None)
    assets_user = models.CharField(max_length=50, verbose_name='操作用户', default=None)
    assets_content = models.CharField(max_length=100, verbose_name='名称', default=None)
    assets_type = models.CharField(max_length=50, default=None)
    create_time = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='执行时间')

    class Meta:
        db_table = 'opsmanage_log_assets'
        verbose_name = '项目配置操作记录表'
        verbose_name_plural = '项目配置操作记录表'


class Project_Config(models.Model):
    project_repertory_choices = (
        ('git', u'git'),
        ('svn', u'svn'),
    )
    deploy_model_choices = (
        ('branch', u'branch'),
        ('tag', u'tag'),
    )
    project_env = models.CharField(max_length=50, verbose_name='项目环境', default=None)
    project_name = models.CharField(max_length=100, verbose_name='项目名称', default=None)
    project_local_command = models.TextField(blank=True, null=True, verbose_name='部署服务器要执行的命令', default=None)
    project_repo_dir = models.CharField(max_length=100, verbose_name='本地仓库目录', default=None)
    project_dir = models.CharField(max_length=100, verbose_name='代码目录', default=None)
    project_exclude = models.TextField(blank=True, null=True, verbose_name='排除文件', default=None)
    project_address = models.CharField(max_length=100, verbose_name='版本仓库地址', default=None)
    project_uuid = models.CharField(max_length=50, verbose_name='唯一id')
    project_repo_user = models.CharField(max_length=50, verbose_name='仓库用户名', blank=True, null=True)
    project_repo_passwd = models.CharField(max_length=50, verbose_name='仓库密码', blank=True, null=True)
    project_repertory = models.CharField(choices=project_repertory_choices, max_length=10, verbose_name='仓库类型',
                                         default=None)
    project_status = models.SmallIntegerField(verbose_name='是否激活', blank=True, null=True, default=None)
    project_remote_command = models.TextField(blank=True, null=True, verbose_name='部署之后执行的命令', default=None)
    project_user = models.CharField(max_length=50, verbose_name='项目文件宿主', default=None)
    project_model = models.CharField(choices=deploy_model_choices, max_length=10, verbose_name='上线类型', default=None)
    project_audit_group = models.SmallIntegerField(verbose_name='项目授权组', blank=True, null=True, default=None)
    '''自定义权限'''

    class Meta:
        db_table = 'opsmanage_project_config'
        permissions = (
            ("can_read_project_config", "读取项目权限"),
            ("can_change_project_config", "更改项目权限"),
            ("can_add_project_config", "添加项目权限"),
            ("can_delete_project_config", "删除项目权限"),
        )
        unique_together = (("project_env", "project_name"))
        verbose_name = '项目管理表'
        verbose_name_plural = '项目管理表'


class Log_Project_Config(models.Model):
    project_id = models.IntegerField(verbose_name='资产类型id', blank=True, null=True, default=None)
    project_user = models.CharField(max_length=50, verbose_name='操作用户', default=None)
    project_name = models.CharField(max_length=100, verbose_name='名称', default=None)
    project_content = models.CharField(max_length=100, default=None)
    project_branch = models.CharField(max_length=100, default=None, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='执行时间')

    class Meta:
        db_table = 'opsmanage_log_project_config'
        verbose_name = '项目配置操作记录表'
        verbose_name_plural = '项目配置操作记录表'


class Project_Number(models.Model):
    project = models.ForeignKey('Project_Config', related_name='project_number', on_delete=models.CASCADE)
    server = models.CharField(max_length=100, verbose_name='服务器IP', default=None)
    dir = models.CharField(max_length=100, verbose_name='项目目录', default=None)

    class Meta:
        db_table = 'opsmanage_project_number'
        permissions = (
            ("can_read_project_number", "读取项目成员权限"),
            ("can_change_project_number", "更改项目成员权限"),
            ("can_add_project_number", "添加项目成员权限"),
            ("can_delete_project_number", "删除项目成员权限"),
        )
        unique_together = (("project", "server"))
        verbose_name = '项目成员表'
        verbose_name_plural = '项目成员表'

    def __unicode__(self):
        return '%s' % (self.server)


class Project_Order(models.Model):
    STATUS = (
        (0, '已通过'),
        (1, '已拒绝'),
        (2, '审核中'),
        (3, '已部署'),
    )
    LEVEL = (
        (0, '非紧急'),
        (1, '紧急'),
    )
    order_user = models.CharField(max_length=30, verbose_name='工单申请人')
    order_project = models.ForeignKey('Project_Config', verbose_name='项目id')
    order_subject = models.CharField(max_length=200, verbose_name='工单申请主题')
    order_content = models.TextField(verbose_name='工单申请内容')
    order_branch = models.CharField(max_length=50, blank=True, null=True, verbose_name='分支版本')
    order_comid = models.CharField(max_length=100, blank=True, null=True, verbose_name='版本id')
    order_tag = models.CharField(max_length=50, blank=True, null=True, verbose_name='标签')
    order_audit = models.CharField(max_length=30, verbose_name='部署指派人')
    order_status = models.IntegerField(choices=STATUS, default='审核中', verbose_name='工单状态')
    order_level = models.IntegerField(choices=LEVEL, default='非紧急', verbose_name='工单紧急程度')
    order_cancel = models.TextField(blank=True, null=True, verbose_name='取消原因')
    create_time = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='工单发布时间')
    modify_time = models.DateTimeField(auto_now=True, blank=True, verbose_name='工单最后修改时间')
    '''自定义权限'''

    class Meta:
        db_table = 'opsmanage_project_order'
        permissions = (
            ("can_read_project_order", "读取项目部署权限"),
            ("can_change_project_order", "更改项目部署权限"),
            ("can_add_project_order", "添加项目部署权限"),
            ("can_delete_project_order", "删除项目部署权限"),
        )
        unique_together = (("order_project", "order_subject", "order_user"))
        verbose_name = '项目部署工单表'
        verbose_name_plural = '项目部署工单表'


class Cron_Config(models.Model):
    cron_server = models.ForeignKey('Server_Assets')
    cron_minute = models.CharField(max_length=10, verbose_name='分', default=None)
    cron_hour = models.CharField(max_length=10, verbose_name='时', default=None)
    cron_day = models.CharField(max_length=10, verbose_name='天', default=None)
    cron_week = models.CharField(max_length=10, verbose_name='周', default=None)
    cron_month = models.CharField(max_length=10, verbose_name='月', default=None)
    cron_user = models.CharField(max_length=50, verbose_name='任务用户', default=None)
    cron_name = models.CharField(max_length=100, verbose_name='任务名称', default=None)
    cron_desc = models.CharField(max_length=200, blank=True, null=True, verbose_name='任务描述', default=None)
    cron_command = models.CharField(max_length=200, verbose_name='任务参数', default=None)
    cron_script = models.FileField(upload_to='./upload/cron/', blank=True, null=True, verbose_name='脚本路径', default=None)
    cron_script_path = models.CharField(max_length=100, blank=True, null=True, verbose_name='脚本路径', default=None)
    cron_status = models.SmallIntegerField(verbose_name='任务状态', default=None)

    class Meta:
        db_table = 'opsmanage_cron_config'
        permissions = (
            ("can_read_cron_config", "读取任务配置权限"),
            ("can_change_cron_config", "更改任务配置权限"),
            ("can_add_cron_config", "添加任务配置权限"),
            ("can_delete_cron_config", "删除任务配置权限"),
        )
        verbose_name = '任务配置表'
        verbose_name_plural = '任务配置表'
        unique_together = (("cron_name", "cron_server", "cron_user"))


class Log_Cron_Config(models.Model):
    cron_id = models.IntegerField(verbose_name='id', blank=True, null=True, default=None)
    cron_user = models.CharField(max_length=50, verbose_name='操作用户', default=None)
    cron_name = models.CharField(max_length=100, verbose_name='名称', default=None)
    cron_content = models.CharField(max_length=100, default=None)
    cron_server = models.CharField(max_length=100, default=None)
    create_time = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='执行时间')

    class Meta:
        db_table = 'opsmanage_log_cron_config'
        verbose_name = '任务配置操作记录表'
        verbose_name_plural = '任务配置操作记录表'


class Log_Ansible_Model(models.Model):
    ans_user = models.CharField(max_length=50, verbose_name='使用用户', default=None)
    ans_model = models.CharField(max_length=100, verbose_name='模块名称', default=None)
    ans_args = models.CharField(max_length=500, blank=True, null=True, verbose_name='模块参数', default=None)
    ans_server = models.TextField(verbose_name='服务器', default=None)
    create_time = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='执行时间')

    class Meta:
        db_table = 'opsmanage_log_ansible_model'
        permissions = (
            ("can_read_log_ansible_model", "读取Ansible模块执行记录权限"),
            ("can_change_log_ansible_model", "更改Ansible模块执行记录权限"),
            ("can_add_log_ansible_model", "添加Ansible模块执行记录权限"),
            ("can_delete_log_ansible_model", "删除Ansible模块执行记录权限"),
        )
        verbose_name = 'Ansible模块执行记录表'
        verbose_name_plural = 'Ansible模块执行记录表'


class Ansible_Playbook(models.Model):
    type = (
        ('service', u'service'),
        ('group', u'group'),
        ('custom', u'custom'),
    )
    # tf_playbook = models.ForeignKey('TF_Playbook_Config')
    playbook_name = models.CharField(max_length=50, verbose_name='剧本名称', unique=True)
    playbook_desc = models.CharField(max_length=200, verbose_name='功能描述', blank=True, null=True)
    playbook_vars = models.TextField(verbose_name='模块参数', blank=True, null=True)
    playbook_uuid = models.CharField(max_length=50, verbose_name='唯一id')
    playbook_server_model = models.CharField(choices=type, verbose_name='服务器选择类型', max_length=10, blank=True, null=True)
    playbook_server_value = models.SmallIntegerField(verbose_name='服务器选择类型值', blank=True, null=True)
    playbook_file = models.CharField(max_length=100, verbose_name='剧本路径')
    playbook_auth_group = models.CharField(max_length=128, verbose_name='授权组', blank=True, null=True)
    playbook_auth_user = models.SmallIntegerField(verbose_name='授权用户', blank=True, null=True, )
    update_time = models.DateTimeField(auto_now=True, blank=True, verbose_name='playbook最后更新时间')
    playbook_type = models.SmallIntegerField(verbose_name='playbook类型', blank=True, null=True)
    forks = models.SmallIntegerField(verbose_name='forks', blank=True, null=True)
    check = models.SmallIntegerField(verbose_name='check', blank=True, null=True)
    playbook_os_type = models.CharField(max_length=128, verbose_name='playbook过滤操作系统类型', blank=True, null=True,
                                        default=None)
    playbook_db_type = models.CharField(max_length=128, verbose_name='playbook过滤数据库类型', blank=True, null=True,
                                        default=None)
    playbook_middleware_type = models.CharField(max_length=128, verbose_name='playbook过滤中间件类型', blank=True, null=True,
                                                default=None)

    class Meta:
        db_table = 'opsmanage_ansible_playbook'
        permissions = (
            ("can_read_ansible_playbook", "读取Ansible剧本权限"),
            ("can_change_ansible_playbook", "更改Ansible剧本权限"),
            ("can_add_ansible_playbook", "添加Ansible剧本权限"),
            ("can_delete_ansible_playbook", "删除Ansible剧本权限"),
        )
        verbose_name = 'Ansible剧本配置表'
        verbose_name_plural = 'Ansible剧本配置表'


class Log_Ansible_Playbook(models.Model):
    ans_id = models.IntegerField(verbose_name='id', blank=True, null=True, default=None)
    ans_user = models.CharField(max_length=50, verbose_name='使用用户', default=None)
    ans_name = models.CharField(max_length=100, verbose_name='模块名称', default=None)
    ans_content = models.CharField(max_length=100, default=None)
    ans_server = models.TextField(verbose_name='服务器', default=None)
    create_time = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='执行时间')

    class Meta:
        db_table = 'opsmanage_log_ansible_playbook'
        verbose_name = 'Ansible剧本操作记录表'
        verbose_name_plural = 'Ansible剧本操作记录表'


class Ansible_Playbook_Number(models.Model):
    playbook = models.ForeignKey('Ansible_Playbook', related_name='server_number', on_delete=models.CASCADE)
    playbook_server = models.CharField(max_length=100, verbose_name='目标服务器', blank=True, null=True)

    class Meta:
        db_table = 'opsmanage_ansible_playbook_number'
        permissions = (
            ("can_read_ansible_playbook_number", "读取Ansible剧本成员权限"),
            ("can_change_ansible_playbook_number", "更改Ansible剧本成员权限"),
            ("can_add_ansible_playbook_number", "添加Ansible剧本成员权限"),
            ("can_delete_ansible_playbook_number", "删除Ansible剧本成员权限"),
        )
        verbose_name = 'Ansible剧本成员表'
        verbose_name_plural = 'Ansible剧本成员表'

    def __unicode__(self):
        return '%s' % (self.playbook_server)


class Global_Config(models.Model):
    ansible_model = models.SmallIntegerField(verbose_name='是否开启ansible模块操作记录', blank=True, null=True)
    ansible_playbook = models.SmallIntegerField(verbose_name='是否开启ansible剧本操作记录', blank=True, null=True)
    cron = models.SmallIntegerField(verbose_name='是否开启计划任务操作记录', blank=True, null=True)
    project = models.SmallIntegerField(verbose_name='是否开启项目操作记录', blank=True, null=True)
    assets = models.SmallIntegerField(verbose_name='是否开启资产操作记录', blank=True, null=True)
    server = models.SmallIntegerField(verbose_name='是否开启服务器命令记录', blank=True, null=True)
    email = models.SmallIntegerField(verbose_name='是否开启邮件通知', blank=True, null=True)
    tf_model_log = models.SmallIntegerField(verbose_name='是否开启谢寅指定日志操作模式', blank=True, null=True)

    class Meta:
        db_table = 'opsmanage_global_config'


class Email_Config(models.Model):
    site = models.CharField(max_length=100, verbose_name='部署站点')
    host = models.CharField(max_length=100, verbose_name='邮件发送服务器')
    port = models.SmallIntegerField(verbose_name='邮件发送服务器端口')
    user = models.CharField(max_length=100, verbose_name='发送用户账户')
    passwd = models.CharField(max_length=100, verbose_name='发送用户密码')
    subject = models.CharField(max_length=100, verbose_name='发送邮件主题标识', default=u'[OPS]')
    cc_user = models.TextField(verbose_name='抄送用户列表', blank=True, null=True)

    class Meta:
        db_table = 'opsmanage_email_config'


class Server_Command_Record(models.Model):
    user = models.CharField(max_length=50, verbose_name='远程用户')
    server = models.CharField(max_length=50, verbose_name='服务器IP')
    client = models.CharField(max_length=50, verbose_name='客户机IP', blank=True, null=True)
    command = models.TextField(verbose_name='历史命令', blank=True, null=True)
    etime = models.CharField(max_length=50, verbose_name='命令执行时间', unique=True)

    class Meta:
        db_table = 'opsmanage_server_command_record'
        permissions = (
            ("can_read_server_command_record", "读取服务器操作日志权限"),
            ("can_change_server_command_record", "更改服务器操作日志权限"),
            ("can_add_server_command_record", "添加服务器操作日志权限"),
            ("can_delete_server_command_record", "删除服务器操作日志权限"),
        )
        verbose_name = '服务器操作日志表'
        verbose_name_plural = '服务器操作日志表'


class Ansible_CallBack_Model_Result(models.Model):
    logId = models.ForeignKey('Log_Ansible_Model')
    content = models.TextField(verbose_name='输出内容', blank=True, null=True)
    content1 = models.TextField(verbose_name='输出内容', blank=True, null=True)
    device_id = models.CharField(max_length=100, verbose_name='所属设备ID')
    result = models.SmallIntegerField(verbose_name='运行结果', blank=True, null=True)


class Ansible_CallBack_PlayBook_Result(models.Model):
    logId = models.ForeignKey('Log_Ansible_Playbook')
    content = models.TextField(verbose_name='输出内容', blank=True, null=True)
    status = models.SmallIntegerField(verbose_name='playbook 运行状态', blank=True, null=True)
    run_time = models.DateTimeField(auto_now_add=True, verbose_name='运行时间', blank=True, null=True)

    class Meta:
        db_table = 'OpsManage_ansible_callback_playbook_result'


class TF_Device_Info(models.Model):
    device_id = models.CharField(max_length=100, verbose_name='所属设备ID', primary_key=True)
    platform_id = models.IntegerField(verbose_name='输出内容', blank=True, null=True)
    platform_name = models.CharField(max_length=100, verbose_name='平台名称')
    ansible_ssh_host = models.CharField(max_length=20, verbose_name='Ansible SSH主机地址', blank=True, null=True)
    ansible_ssh_port = models.SmallIntegerField(verbose_name='Ansible SSH端口', blank=True, null=True)
    ansible_ssh_user = models.CharField(max_length=32, verbose_name='Ansible SSH账号', blank=True, null=True)
    ansible_ssh_pass = models.CharField(max_length=32, verbose_name='Ansible SSH密码', blank=True, null=True)
    ansible_ssh_private_key_file = models.TextField(verbose_name='Ansible SSH私钥', blank=True, null=True)

    class Meta:
        db_table = 'tf_device_info'
        permissions = (
            ("can_read_tf_device_info", "读取设备基础信息表权限"),
            ("can_change_tf_device_info", "更改设备基础信息表权限"),
            ("can_add_tf_device_info", "添加设备基础信息表权限"),
            ("can_delete_tf_device_info", "删除设备基础信息表权限"),
        )
        verbose_name = '设备基础信息表'
        verbose_name_plural = '设备基础信息表'


class TF_Asset_Hard_Info(models.Model):
    asset_id = models.CharField(max_length=100, verbose_name='资产ID', primary_key=True)
    device_id = models.ForeignKey('TF_Device_Info', related_name="hardinfo")
    hd_equipment_type = models.CharField(max_length=128, verbose_name='设备型号', blank=True, null=True)
    hd_serial_no = models.CharField(max_length=128, verbose_name='设备序列号', blank=True, null=True)
    hd_cpu_model = models.CharField(max_length=128, verbose_name='CPU型号', blank=True, null=True)
    hd_cpu_count = models.IntegerField(verbose_name='CPU个数', blank=True, null=True)
    hd_per_cpu_thread = models.TextField(verbose_name='单个CPU线程', blank=True, null=True)
    hd_cpu_kernel_count = models.IntegerField(verbose_name='CPU核数', blank=True, null=True)
    hd_can_max_mem = models.IntegerField(verbose_name='设备支持最大内存', blank=True, null=True)
    hd_mem_slot_count = models.SmallIntegerField(verbose_name='设备内存插槽数', blank=True, null=True)
    hd_mem_count = models.SmallIntegerField(verbose_name='内存条数', blank=True, null=True)
    hd_per_mem_vendor = models.TextField(verbose_name='单内存厂商', blank=True, null=True)
    hd_per_mem_type = models.TextField(verbose_name='单内存类型', blank=True, null=True)
    hd_per_mem_rate = models.TextField(verbose_name='单内存速率', blank=True, null=True)
    hd_per_mem_size = models.TextField(verbose_name='单内存大小', blank=True, null=True)
    hd_local_hd_count = models.SmallIntegerField(verbose_name='本地硬盘数', blank=True, null=True)
    hd_local_disk_size = models.TextField(verbose_name='本地硬盘大小', blank=True, null=True)
    hd_local_hd_model = models.TextField(verbose_name='本地硬盘型号', blank=True, null=True)
    hd_nwcard_count = models.SmallIntegerField(verbose_name='网卡数', blank=True, null=True)
    hd_per_nwcard_mac = models.TextField(verbose_name='单个网卡MAC', blank=True, null=True)
    hd_per_nwcard_ip = models.TextField(verbose_name='单个网卡IP', blank=True, null=True)
    hd_sper_nwcard_mask = models.TextField(verbose_name='单个网卡IP掩码', blank=True, null=True)
    hd_hba_count = models.SmallIntegerField(verbose_name='HBA卡数', blank=True, null=True)
    hd_per_hba_port = models.TextField(verbose_name='单个HBA卡端口号', blank=True, null=True)
    hd_per_hba_rate = models.TextField(verbose_name='单个HBA卡速率', blank=True, null=True)
    hd_have_cdrom = models.SmallIntegerField(verbose_name='是否有光驱', blank=True, null=True)
    hd_cdrom_type = models.TextField(verbose_name='光驱类型', blank=True, null=True)
    hd_usb_speed = models.TextField(verbose_name='USB接口速率', blank=True, null=True)
    os_type = models.CharField(max_length=128, verbose_name='操作系统类型', blank=True, null=True)
    os_architecture = models.CharField(max_length=128, verbose_name='操作系统架构', blank=True, null=True)
    os_version = models.CharField(max_length=128, verbose_name='操作系统版本', blank=True, null=True)
    os_file_type = models.CharField(max_length=128, verbose_name='文件系统类型', blank=True, null=True)
    os_memory_used_rate = models.SmallIntegerField(verbose_name='内存占用率', blank=True, null=True)
    acl_selinux_state = models.CharField(max_length=16, verbose_name='SELinux状态', blank=True, null=True)
    record_time = models.DateTimeField(auto_now_add=True, verbose_name='数据采集时间')

    class Meta:
        db_table = 'tf_asset_hard_info'
        permissions = (
            ("can_read_tf_asset_hard_info", "读取设备资产信息表权限"),
            ("can_change_tf_asset_hard_info", "更改设备资产信息表权限"),
            ("can_add_tf_asset_hard_info", "添加设备资产信息表权限"),
            ("can_delete_tf_asset_hard_info", "删除设备资产信息表权限"),
        )
        verbose_name = '设备资产信息表'
        verbose_name_plural = '设备资产信息表'


class TF_Asset_Soft_Info(models.Model):
    sw_type_choices = (
        ('0', u'数据库'),
        ('1', u'应用软件'),
    )
    soft_asset_id = models.CharField(max_length=100, verbose_name='资产ID', primary_key=True)
    device_id = models.ForeignKey('TF_Device_Info', related_name="softinfo")
    sw_type = models.SmallIntegerField(choices=sw_type_choices, verbose_name='0:通用软件;  1:应用软件')
    sw_name = models.CharField(max_length=128, verbose_name='软件名称')
    sw_version = models.CharField(max_length=128, verbose_name='软件版本', blank=True, null=True)
    sw_install_path = models.CharField(max_length=255, verbose_name='软件安装路径', blank=True, null=True)
    sw_conf_file_path = models.CharField(max_length=255, verbose_name='软件配置文件路径', blank=True, null=True)
    record_time = models.DateTimeField(auto_now_add=True, verbose_name='数据采集时间')

    class Meta:
        db_table = 'tf_asset_soft_info'
        permissions = (
            ("can_read_tf_asset_soft_info", "读取软件资产信息表权限"),
            ("can_change_tf_asset_soft_info", "更改软件资产信息表权限"),
            ("can_add_tf_asset_soft_info", "添加软件资产信息表权限"),
            ("can_delete_tf_asset_soft_info", "删除软件资产信息表权限"),
        )
        verbose_name = '软件资产信息表'
        verbose_name_plural = '软件资产信息表'


class TF_Device_Dynamic_Info(models.Model):
    id = models.AutoField(primary_key=True)
    device_id = models.ForeignKey('TF_Device_Info')
    os_time = models.DateTimeField(auto_now_add=True, verbose_name='操作系统当前时间')
    os_file_volume_info = models.TextField(verbose_name='文件系统逻辑卷信息', blank=True, null=True)
    os_file_used = models.SmallIntegerField(verbose_name='文件系统占用率', blank=True, null=True)
    os_file_node_used = models.SmallIntegerField(verbose_name='文件系统节点占用率', blank=True, null=True)
    os_cpu_used_rate = models.SmallIntegerField(verbose_name='CPU利用率', blank=True, null=True)
    os_cpu_idle = models.SmallIntegerField(verbose_name='CPU空闲', blank=True, null=True)
    os_cpu_io_wait = models.SmallIntegerField(verbose_name='CPU I/O wait', blank=True, null=True)
    os_mem_used_size = models.IntegerField(verbose_name='内存占用大小', blank=True, null=True)
    os_swap_size = models.IntegerField(verbose_name='SWAP空间大小', blank=True, null=True)
    os_swap_rate = models.SmallIntegerField(verbose_name='SWAP占用率', blank=True, null=True)
    sw_port_app_pid = models.TextField(verbose_name='开放端口、对应的应用以及进程号', blank=True, null=True)
    acl_routing_count = models.IntegerField(verbose_name='主机路由表条目数', blank=True, null=True)
    acl_routing_table = models.TextField(verbose_name='主机路由表条目', blank=True, null=True)
    acl_Hosts_allow_table = models.TextField(verbose_name='hosts.allow条目', blank=True, null=True)
    acl_Hosts_deny_table = models.TextField(verbose_name='hosts.deny条目', blank=True, null=True)
    acl_Iptables_table = models.TextField(verbose_name='iptables条目', blank=True, null=True)
    acl_IPF_table = models.TextField(verbose_name='IPF条目', blank=True, null=True)
    acl_SSH_blacklist = models.TextField(verbose_name='SSH黑名单', blank=True, null=True)
    acl_Sudoers_conf = models.TextField(verbose_name='sudoers配置', blank=True, null=True)
    acl_Tocmat_table = models.TextField(verbose_name='tocmat访问控制条目', blank=True, null=True)
    acl_Apache_table = models.TextField(verbose_name='apache访问控制条目', blank=True, null=True)
    acl_Nginx_table = models.TextField(verbose_name='nginx访问控制条目', blank=True, null=True)
    acl_Weblogic_table = models.TextField(verbose_name='WebLogic访问控制条目', blank=True, null=True)
    acl_WebSphere_table = models.TextField(verbose_name='WebSphere访问控制条目', blank=True, null=True)
    acl_JBoss_table = models.TextField(verbose_name='JBoss访问控制条目', blank=True, null=True)
    acl_Resin_table = models.TextField(verbose_name='Resin访问控制条目', blank=True, null=True)
    acl_Axis_table = models.TextField(verbose_name='Axis访问控制条目', blank=True, null=True)
    acl_Axis2_table = models.TextField(verbose_name='Axis2访问控制条目', blank=True, null=True)
    acl_Oracle_table = models.TextField(verbose_name='Oracle访问控制条目', blank=True, null=True)
    acl_MySQL_table = models.TextField(verbose_name='MySQL访问控制条目', blank=True, null=True)
    acl_Sybase_table = models.TextField(verbose_name='sybase访问控制条目', blank=True, null=True)
    acl_DB2_table = models.TextField(verbose_name='DB2访问控制条目', blank=True, null=True)
    acl_Sqlserver_table = models.TextField(verbose_name='SQLServer访问控制条目', blank=True, null=True)
    acl_PostgreSQL_table = models.TextField(verbose_name='PostgreSQL访问控制条目', blank=True, null=True)
    log_History_op_table = models.TextField(verbose_name='history操作条目', blank=True, null=True)
    lh_hrisk_scan = models.TextField(verbose_name='扫描中高危漏洞分布', blank=True, null=True)
    lh_hrisk_penetration = models.TextField(verbose_name='渗透中高危漏洞分布', blank=True, null=True)
    bl_os_rate = models.SmallIntegerField(verbose_name='操作系统加固完成率', blank=True, null=True)
    bl_middleware_rate = models.SmallIntegerField(verbose_name='中间件加固完成率', blank=True, null=True)
    bl_db_rate = models.SmallIntegerField(verbose_name='数据库加固完成率', blank=True, null=True)
    clock = models.IntegerField(verbose_name='启动采集时的时钟，分区字段，每天一个分区')

    class Meta:
        db_table = 'tf_device_dynamic_info'
        permissions = (
            ("can_read_tf_device_dynamic_info", "读取动态设备资产信息表权限"),
            ("can_change_tf_device_dynamic_info", "更改动态设备资产信息表权限"),
            ("can_add_tf_device_dynamic_info", "添加动态设备资产信息表权限"),
            ("can_delete_tf_device_dynamic_info", "删除动态设备资产信息表权限"),
        )
        verbose_name = '动态设备资产信息表'
        verbose_name_plural = '动态设备资产信息表'


class TF_Playbook_Config(models.Model):
    id = models.AutoField(primary_key=True)
    playbook_name = models.CharField(max_length=128, verbose_name='剧本名称')
    playbook_desc = models.CharField(max_length=512, verbose_name='功能描述', blank=True, null=True)
    playbook_path = models.CharField(max_length=128, verbose_name='剧本路径')
    playbook_file_name = models.CharField(max_length=128, verbose_name='剧本文件名')
    playbook_type = models.SmallIntegerField(verbose_name='剧本类型')
    update_time = models.DateTimeField(auto_now=True, blank=True, verbose_name='playbook最后更新时间')

    class Meta:
        db_table = 'tf_playbook_config'
        permissions = (
            ("can_read_tf_playbook_config", "读取剧本配置表权限"),
            ("can_change_tf_playbook_config", "更改剧本配置表权限"),
            ("can_add_tf_playbook_config", "添加剧本配置表权限"),
            ("can_delete_tf_playbook_config", "删除剧本配置表权限"),
        )
        verbose_name = '剧本配置表'
        verbose_name_plural = '剧本配置表'


class TF_Asset_Port_Info(models.Model):
    device = models.ForeignKey('TF_Device_Info')
    groupname = models.CharField(max_length=255, verbose_name='组名名称')
    stream_type = models.CharField(max_length=3, verbose_name='类型', blank=True, null=True)
    listen_ip = models.CharField(max_length=40, verbose_name='ip', blank=True, null=True)
    listen_port = models.CharField(max_length=5, verbose_name='端口', blank=True, null=True)
    process = models.TextField(verbose_name='进程', blank=True, null=True)
    date = models.DateTimeField(auto_now=True, blank=True, verbose_name='最后更新时间')

    class Meta:
        db_table = 'tf_asset_port_info'
        permissions = (
            ("can_read_tf_asset_port_info", "读取资产端口信息表权限"),
            ("can_change_tf_asset_port_info", "更改资产端口信息表权限"),
            ("can_add_tf_asset_port_info", "添加资产端口信息表权限"),
            ("can_delete_tf_asset_port_info", "删除资产端口信息表权限"),
        )
        verbose_name = '资产端口信息表'
        verbose_name_plural = '资产端口信息表'


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
