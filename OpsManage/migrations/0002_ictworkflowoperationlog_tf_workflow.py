# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2018-04-18 15:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OpsManage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IctWorkflowOperationLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='TF_Workflow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('workflow_desc', models.CharField(blank=True, max_length=512, null=True, verbose_name=b'Workflow\xe6\x8f\x8f\xe8\xbf\xb0')),
                ('workflow_path', models.CharField(max_length=128, verbose_name=b'Workflow\xe8\xb7\xaf\xe5\xbe\x84')),
                ('workflow_filename', models.CharField(max_length=128, verbose_name=b'Workflow\xe6\x96\x87\xe4\xbb\xb6\xe5\x90\x8d')),
                ('workflow_name', models.CharField(max_length=100, verbose_name=b'Workflow\xe4\xbb\xbb\xe5\x8a\xa1\xe5\x90\x8d')),
                ('content', models.CharField(max_length=512, null=True, verbose_name=b'\xe6\x93\x8d\xe4\xbd\x9c\xe5\x86\x85\xe5\xae\xb9')),
                ('oper_user', models.CharField(max_length=32, verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4')),
            ],
            options={
                'db_table': 'ict_workflow_operation_log',
            },
        ),
    ]