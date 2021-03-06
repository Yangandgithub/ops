#!/usr/bin/env python  
# _#_ coding:utf-8 _*_  
from rest_framework import serializers
from OpsManage.models import *
from django.contrib.auth.models import Group, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'last_login', 'is_superuser', 'username',
                  'first_name', 'last_name', 'email', 'is_staff',
                  'is_active', 'date_joined')


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service_Assets
        fields = ('id', 'service_name')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone_Assets
        fields = ('id', 'zone_name')


class LineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line_Assets
        fields = ('id', 'line_name')


class RaidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Raid_Assets
        fields = ('id', 'raid_name')

        # class AssetStatusSerializer(serializers.ModelSerializer):


# class Meta:
#         model = Assets_Satus
#         fields = ('id','status_name') 

class CronSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cron_Config
        fields = ('id', 'cron_minute', 'cron_hour', 'cron_day',
                  'cron_week', 'cron_month', 'cron_user',
                  'cron_name', 'cron_desc', 'cron_server',
                  'cron_command', 'cron_script', 'cron_status')


class AssetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assets
        fields = ('id', 'assets_type', 'name', 'sn', 'buy_time', 'expire_date',
                  'buy_user', 'management_ip', 'manufacturer', 'provider',
                  'model', 'status', 'put_zone', 'group', 'business')


class AssetsLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log_Assets
        fields = ('id', 'assets_id', 'assets_user', 'assets_content', 'assets_type', 'create_time')


class ProjectConfigSerializer(serializers.ModelSerializer):
    project_number = serializers.StringRelatedField(many=True)

    class Meta:
        model = Project_Config
        fields = ('id', 'project_env', 'project_name', 'project_local_command',
                  'project_repo_dir', 'project_dir', 'project_exclude',
                  'project_address', 'project_repertory', 'project_status',
                  'project_remote_command', 'project_number')


class DeployLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log_Project_Config
        fields = ('id', 'project_id', 'project_user', 'project_name',
                  'project_content', 'project_branch', 'create_time')


class AnbiblePlaybookSerializer(serializers.ModelSerializer):
    server_number = serializers.StringRelatedField(many=True)

    class Meta:
        model = Ansible_Playbook
        fields = ('id', 'playbook_name', 'playbook_desc', 'playbook_vars',
                  'playbook_uuid', 'playbook_file', 'playbook_auth_group',
                  'playbook_auth_user', 'server_number', 'update_time', 'playbook_type', 'forks', 'check')


class AnsibleModelLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log_Ansible_Model
        fields = ('id', 'ans_user', 'ans_model', 'ans_args',
                  'ans_server', 'create_time')


class AnsiblePlaybookLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log_Ansible_Playbook
        fields = ('id', 'ans_user', 'ans_name', 'ans_content', 'ans_id',
                  'ans_server', 'ans_content', 'create_time')


class CronLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log_Cron_Config
        fields = ('id', 'cron_id', 'cron_user', 'cron_name', 'cron_content',
                  'cron_server', 'create_time')


class ServerSerializer(serializers.ModelSerializer):
    assets = AssetsSerializer(required=False)

    #     keyfile = serializers.FileField(max_length=None, use_url=True)
    class Meta:
        model = Server_Assets
        fields = ('id', 'ip', 'hostname', 'username', 'port', 'passwd',
                  'line', 'cpu', 'cpu_number', 'vcpu_number', 'keyfile',
                  'cpu_core', 'disk_total', 'ram_total', 'kernel',
                  'selinux', 'swap', 'raid', 'system', 'assets')

    def create(self, data):
        if (data.get('assets')):
            assets_data = data.pop('assets')
            assets = Assets.objects.create(**assets_data)
        else:
            assets = Assets()
        data['assets'] = assets;
        server = Server_Assets.objects.create(**data)
        return server


class NetworkSerializer(serializers.ModelSerializer):
    assets = AssetsSerializer(required=False)

    class Meta:
        model = Network_Assets
        fields = ('id', 'ip', 'bandwidth', 'port_number', 'firmware',
                  'cpu', 'stone', 'configure_detail', 'assets')

    def create(self, data):
        if (data.get('assets')):
            assets_data = data.pop('assets')
            assets = Assets.objects.create(**assets_data)
        else:
            assets = Assets()
        data['assets'] = assets;
        server = Network_Assets.objects.create(**data)
        return server


class DeployOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project_Order
        fields = ('id', 'order_project', 'order_subject', 'order_content',
                  'order_branch', 'order_comid', 'order_tag', 'order_audit',
                  'order_status', 'order_level', 'order_cancel', 'create_time',
                  'order_user')


class TFDeviceInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TF_Device_Info
        fields = (
            'device_id', 'platform_id', 'platform_name', 'ansible_ssh_host',
            'ansible_ssh_port', 'ansible_ssh_user', 'ansible_ssh_pass', 'ansible_ssh_private_key_file')


class TfAssetSoftInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TF_Asset_Soft_Info
        fields = (
            'soft_asset_id', 'device_id', 'sw_type', 'sw_name', 'sw_version', 'sw_install_path', 'sw_conf_file_path',
            'record_time')


class TfDeviceDynamicInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TF_Device_Dynamic_Info
        fields = (
            'id', 'device_id', 'os_time', 'os_file_volume_info', 'os_file_used', 'os_file_node_used',
            'os_cpu_used_rate',
            'os_cpu_idle', 'os_cpu_io_wait', 'os_mem_used_size', 'os_swap_size', 'os_swap_rate', 'sw_port_app_pid',
            'acl_routing_count',
            'acl_routing_table', 'acl_Hosts_allow_table', 'acl_Hosts_deny_table', 'acl_Iptables_table', 'acl_IPF_table',
            'acl_SSH_blacklist',
            'acl_Sudoers_conf', 'acl_Tocmat_table', 'acl_Apache_table', 'acl_Nginx_table', 'acl_Weblogic_table',
            'acl_WebSphere_table', 'acl_JBoss_table',
            'acl_Resin_table', 'acl_Axis_table', 'acl_Axis2_table', 'acl_Oracle_table', 'acl_MySQL_table',
            'acl_Sybase_table', 'acl_DB2_table', 'acl_Sqlserver_table',
            'acl_PostgreSQL_table', 'log_History_op_table', 'lh_hrisk_scan',
            'lh_hrisk_penetration', 'bl_os_rate', 'bl_middleware_rate', 'bl_db_rate', 'clock')


class TfAssetHardInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TF_Asset_Hard_Info
        fields = (
            'asset_id', 'device_id', 'hd_equipment_type', 'hd_serial_no', 'hd_cpu_model', 'hd_cpu_count',
            'hd_per_cpu_thread',
            'hd_cpu_kernel_count', 'hd_can_max_mem', 'hd_mem_slot_count', 'hd_mem_count', 'hd_per_mem_vendor',
            'hd_per_mem_type',
            'hd_per_mem_rate', 'hd_per_mem_size', 'hd_local_hd_count', 'hd_local_disk_size', 'hd_local_hd_model',
            'hd_nwcard_count',
            'hd_per_nwcard_mac', 'hd_per_nwcard_ip', 'hd_sper_nwcard_mask', 'hd_hba_count', 'hd_per_hba_port',
            'hd_per_hba_rate', 'hd_have_cdrom',
            'hd_cdrom_type', 'hd_usb_speed', 'os_type', 'os_architecture', 'os_version', 'os_file_type',
            'os_memory_used_rate', 'acl_selinux_state', 'record_time')


class TfPlaybookConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = TF_Playbook_Config
        fields = (
            'id', 'playbook_name', 'playbook_desc', 'playbook_path', 'playbook_file_name', 'playbook_type',
            'update_time')


class TfAssetPortInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TF_Asset_Port_Info
        fields = (
            'device', 'groupname', 'stream_type', 'listen_ip', 'listen_port', 'process',
            'date')
