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
from django.contrib.auth.decorators import permission_required
from django.db.models import Sum, Count


@api_view(['GET', 'PUT'])
@permission_required('OpsManage.can_read_tf_asset_soft_info', raise_exception=True)
def tf_asset_soft_num(request, type, format=None):
    try:
        snippet = TF_Asset_Soft_Info.objects.filter(sw_type=type).values('sw_name').annotate(sw_sum=Count('sw_name'))
    except TF_Asset_Soft_Info.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        data = []
        for item in snippet:
            tmp = {}
            tmp['sw_name'] = item['sw_name']
            tmp['sw_sum'] = item['sw_sum']
            data.append(tmp)
        return Response(data)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_required('OpsManage.can_read_tf_asset_soft_info', raise_exception=True)
def tf_asset_soft_name(request, name, format=None):
    try:
        snippet = TF_Asset_Soft_Info.objects.filter(sw_name=name)
    except TF_Asset_Soft_Info.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TfAssetSoftInfoSerializer(snippet, many=True)
        return Response(serializer.data)
