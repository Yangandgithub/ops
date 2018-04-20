#!/usr/bin/env python
# _#_ coding:utf-8 _*_
from rest_framework import viewsets, permissions
from OpsManage.serializers import *
from OpsManage.models import *
from rest_framework import status
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from OpsManage.tasks import recordAssets
from django.contrib.auth.decorators import permission_required
from django.db.models import Sum, Count


@api_view(['GET', 'DELETE'])
@permission_required('OpsManage.can_read_tf_asset_hard_info', raise_exception=True)
def tf_asset_hard_num(request, format=None):
    try:
        snippet = TF_Asset_Hard_Info.objects.all().values('os_type').annotate(os_sum=Count('os_type'))
    except TF_Asset_Hard_Info.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        data = []
        for item in snippet:
            tmp = {}
            tmp['os_type'] = item['os_type']
            tmp['os_sum'] = item['os_sum']
            data.append(tmp)
        return Response(data)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_required('OpsManage.can_read_tf_asset_hard_info', raise_exception=True)
def tf_asset_hard_info(request, id, format=None):
    try:
        snippet = TF_Asset_Hard_Info.objects.filter(asset_id=id)
    except TF_Asset_Hard_Info.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TfAssetHardInfoSerializer(snippet, many=True)
        return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_required('OpsManage.can_read_tf_device_dynamic_info', raise_exception=True)
def tf_device_dynamic_info(request, id, format=None):
    try:
        snippet = TF_Device_Dynamic_Info.objects.filter(id=id)
    except TF_Device_Dynamic_Info.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TfDeviceDynamicInfoSerializer(snippet, many=True)
        return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_required('OpsManage.can_read_tf_device_info', raise_exception=True)
def tf_device_info(request, id, format=None):
    try:
        if id.strip() == '0':
            snippet = TF_Device_Info.objects.all()
        else:
            snippet = TF_Device_Info.objects.filter(platform_id=id)
    except TF_Device_Info.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TFDeviceInfoSerializer(snippet, many=True)
        return Response(serializer.data)
