#!/usr/bin/env python
# _#_ coding:utf-8 _*_
from OpsManage.serializers import *
from OpsManage.models import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import permission_required


@api_view(['GET', 'PUT', 'DELETE'])
@permission_required('OpsManage.can_read_tf_playbook_config', raise_exception=True)
def tf_playbook_config(request, id, format=None):
    try:
        if id.strip() == '0':
            snippet = TF_Playbook_Config.objects.all()
        else:
            snippet = TF_Playbook_Config.objects.filter(playbook_type=id)
    except TF_Playbook_Config.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TfPlaybookConfigSerializer(snippet, many=True)
        return Response(serializer.data)
