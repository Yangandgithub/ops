#!/usr/bin/env python
# _#_ coding:utf-8 _*_
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import permission_required


@login_required()
def role_management(request):
    if request.method == 'GET':
        return render_to_response('roles/roles.html', context_instance=RequestContext(request))
