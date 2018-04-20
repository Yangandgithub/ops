#!/usr/bin/env python  
# _#_ coding:utf-8 _*_
import random, string
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
from django.http import HttpResponse, Http404
from datetime import time
from MySQLdb import connections
from OpsManage.utils import base
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render_to_response
from django.contrib import auth
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Q, Count
import time
from django.contrib.auth.models import User
from OpsManage.models import (Global_Config, Email_Config, Assets,
                              Cron_Config, Project_Order, Log_Assets,
                              Project_Config, Ansible_Playbook, TF_Asset_Hard_Info,
                              TF_Asset_Soft_Info, Ansible_CallBack_PlayBook_Result,
                              TF_Playbook_Config)
from django.contrib.auth.decorators import permission_required


def homepage(request):
    return render_to_response('login.html', context_instance=RequestContext(request))


# @login_required(login_url='/login')
def index(request):
    if request.session.get('username') is None:
        return HttpResponseRedirect('/login', {"user": request.user})

    # 操作系统类型
    osCount = TF_Asset_Hard_Info.objects.all().count()
    # 操作系统类型
    osTypeList = TF_Asset_Hard_Info.objects.all().values('os_type').annotate(os_count=Count('os_type'))
    AIX = 0
    CentOS = 0
    HP = 0
    RedHat = 0
    SLES = 0
    Solaris = 0
    for osType in osTypeList:
        if osType['os_type'] == 'AIX':
            AIX = osType['os_count']
        elif osType['os_type'] == 'CentOS':
            CentOS = osType['os_count']
        elif osType['os_type'] == 'HP-UX':
            HP = osType['os_count']
        elif osType['os_type'] == 'RedHat':
            RedHat = osType['os_count']
        elif osType['os_type'] == 'SLES':
            SLES = osType['os_count']
        elif osType['os_type'] == 'Solaris':
            Solaris = osType['os_count']
    osTypeTotal = {
        'AIX': AIX,
        'CentOS': CentOS,
        'HP': HP,
        'RedHat': RedHat,
        'SLES': SLES,
        'Solaris': Solaris
    }
    # 软件类型
    dbCount = TF_Asset_Soft_Info.objects.filter(sw_type='0').count()
    softCount = TF_Asset_Soft_Info.objects.filter(sw_type='1').count()
    # 软件类型
    softTypeList = TF_Asset_Soft_Info.objects.all().values('sw_name').annotate(os_count=Count('sw_name'))
    Oracle = 0
    MySQL = 0
    SqlServer = 0
    DB2 = 0
    Sybase = 0
    PostgreSQL = 0
    Tomcat = 0
    Apache = 0
    nginx = 0
    WebLogic = 0
    WebSphere = 0
    JBoss = 0
    for softType in softTypeList:
        if softType['sw_name'] == 'oracle':
            Oracle = softType['os_count']
        elif softType['sw_name'] == 'mysql':
            MySQL = softType['os_count']
        elif softType['sw_name'] == 'sqlserver':
            SqlServer = softType['os_count']
        elif softType['sw_name'] == 'db2':
            DB2 = softType['os_count']
        elif softType['sw_name'] == 'sybase':
            Sybase = softType['os_count']
        elif softType['sw_name'] == 'postgresql':
            PostgreSQL = softType['os_count']
        elif softType['sw_name'] == 'tomcat':
            Tomcat = softType['os_count']
        elif softType['sw_name'] == 'apache':
            Apache = softType['os_count']
        elif softType['sw_name'] == 'nginx':
            nginx = softType['os_count']
        elif softType['sw_name'] == 'WebLogic':
            WebLogic = softType['os_count']
        elif softType['sw_name'] == 'websphere':
            WebSphere = softType['os_count']
        elif softType['sw_name'] == 'jboss':
            JBoss = softType['os_count']

    softTypeTotal = {
        'dbCount': dbCount,
        'softCount': softCount,
        'Oracle': Oracle,
        'MySQL': MySQL,
        'SqlServer': SqlServer,
        'DB2': DB2,
        'Sybase': Sybase,
        'PostgreSQL': PostgreSQL,
        'Tomcat': Tomcat,
        'Apache': Apache,
        'nginx': nginx,
        'WebLogic': WebLogic,
        'WebSphere': WebSphere,
        'JBoss': JBoss
    }

    # 任务执行分布 图表
    '''
    select = {'day': connection.ops.date_trunc_sql('day', 'run_time')}

    result_success = Ansible_CallBack_PlayBook_Result.objects.filter(status='0').extra(select=select).values(
        'day').annotate(result_count=Count('run_time')).order_by('day')

    result_fail = Ansible_CallBack_PlayBook_Result.objects.filter(status='1').extra(select=select).values(
        'day').annotate(result_count=Count('run_time')).order_by('day')

    categories = []
    for item in result_success:
        if item['day'].strftime("%Y-%m-%d") not in categories:
            categories.append(item['day'].strftime("%Y-%m-%d"))

    for item in result_fail:
        if item['day'].strftime("%Y-%m-%d") not in categories:
            categories.append(item['day'].strftime("%Y-%m-%d"))

    series_success = "["
    for item in result_success:
        if item['day'].strftime("%Y-%m-%d") in categories:
            series_success += str(item['result_count']) + ","
        else:
            series_success += '0,'

    series_fail = "["
    for item in result_fail:
        if item['day'].strftime("%Y-%m-%d") in categories:
            series_fail += str(item['result_count']) + ","
        else:
            series_fail += '0,'

    series_success = series_success[:-1] + "]";
    series_fail = series_fail[:-1] + "]";
    '''
    # 修改任务执行分布统计bug
    select = {'day': connection.ops.date_trunc_sql('day', 'run_time')}
    days = Ansible_CallBack_PlayBook_Result.objects.filter(status__in=(0, 1)).extra(select=select).values(
        'day').annotate(result_count=Count('run_time')).order_by('-day')[0:30]

    result_success = Ansible_CallBack_PlayBook_Result.objects.filter(status=0).extra(select=select).values(
        'day').annotate(result_count=Count('run_time')).order_by('-day')[0:30]

    result_fail = Ansible_CallBack_PlayBook_Result.objects.filter(status=1).extra(select=select).values(
        'day').annotate(result_count=Count('run_time')).order_by('-day')[0:30]

    categories = []
    result = {}
    for item in days:
        if item['day'].strftime("%Y-%m-%d") not in categories:
            categories.append(item['day'].strftime("%Y-%m-%d"))
            result[item['day'].strftime("%Y-%m-%d")] = ['0', '0']

    for item in result_success:
        if item['day'].strftime("%Y-%m-%d") in categories:
            result[item['day'].strftime("%Y-%m-%d")][0] = str(item['result_count'])

    for item in result_fail:
        if item['day'].strftime("%Y-%m-%d") in categories:
            result[item['day'].strftime("%Y-%m-%d")][1] = str(item['result_count'])

    series_success = "["
    series_fail = "["
    categories = categories[::-1]
    for item in categories:
        series_success += str(result[item][0]) + ","
        series_fail += str(result[item][1]) + ","

    series_success = series_success + "]";
    series_fail = series_fail + "]";

    series = {
        "success": series_success,
        "fail": series_fail,
        "categories": categories
    }

    # Playbook情况 图表
    playbookList = TF_Playbook_Config.objects.all().values('playbook_type').annotate(
        type_count=Count('playbook_type')).order_by('playbook_type')
    playbookSeries = "["
    for item in playbookList:
        if str(item['playbook_type']) == '1':
            playbookSeries += '[\'资产信息\','
        elif str(item['playbook_type']) == '2':
            playbookSeries += '[\'基线加固\','
        elif str(item['playbook_type']) == '3':
            playbookSeries += '[\'日志审计\','
        elif str(item['playbook_type']) == '4':
            playbookSeries += '[\'漏洞整改与隐患排查\','
        elif str(item['playbook_type']) == '5':
            playbookSeries += '[\'密码 / 端口检测\','
        elif str(item['playbook_type']) == '6':
            playbookSeries += '[\'安全访问控制\','

        playbookSeries += str(item['type_count']) + '],'

    playbookSeries = playbookSeries[:-1] + "]";
    return render_to_response('index.html', {"osCount": osCount, "osTypeTotal": osTypeTotal,
                                             "softTypeTotal": softTypeTotal, "series": series,
                                             "playbookSeries": playbookSeries},
                              context_instance=RequestContext(request))


def login(request):
    if request.session.get('username') is not None:
        return HttpResponseRedirect('/', {"user": request.user})
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        rand = request.POST.get('rand')
        try:
            check_code = request.session['check_code']
        except:
            check_code = ''
        # 注销session
        request.session['check_code'] = ''
        if check_code != rand:
            if request.method == "POST":
                return render_to_response('login.html', {"login_error_info": "验证码错误！"},
                                          context_instance=RequestContext(request))

        user = auth.authenticate(username=username, password=password)
        if user and user.is_active:
            auth.login(request, user)
            request.session['username'] = username
            return HttpResponseRedirect('/', {"user": request.user})
        else:
            if request.method == "POST":
                return render_to_response('login.html', {"login_error_info": "用户名或者密码错误！"},
                                          context_instance=RequestContext(request))
            else:
                return render_to_response('login.html', context_instance=RequestContext(request))


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/login')


def noperm(request):
    return render_to_response('noperm.html', {"user": request.user}, context_instance=RequestContext(request))


@login_required(login_url='/login')
def dashboard(request):
    # 7天更新频率统计
    userList = Project_Order.objects.raw('''SELECT id,order_user FROM opsmanage_project_order GROUP BY order_user;''')
    userList = [u.order_user for u in userList]
    dateList = [base.getDaysAgo(num) for num in xrange(0, 7)][::-1]  # 将日期反序
    dataList = []
    for user in userList:
        valueList = []
        data = dict()
        for startTime in dateList:
            sql = """SELECT id,IFNULL(count(0),0) as count from opsmanage_project_order WHERE 
                        date_format(create_time,"%%Y%%m%%d") = {startTime} and order_user='{user}'""".format(
                startTime=startTime, user=user)
            userData = Project_Order.objects.raw(sql)
            if userData[0].count == 0:
                valueList.append(random.randint(1, 10))
            else:
                valueList.append(userData[0].count)
        data[user] = valueList
        dataList.append(data)
        # 获取所有指派给自己需要审核的工单
    orderNotice = Project_Order.objects.all().order_by('-id')[0:10]
    # 月度更新频率统计
    monthList = [base.getDaysAgo(num)[0:6] for num in (0, 30, 60, 90, 120, 150, 180)][::-1]
    monthDataList = []
    for ms in monthList:
        startTime = int(ms + '01')
        endTime = int(ms + '31')
        data = dict()
        data['date'] = ms
        for user in userList:
            sql = """SELECT id,IFNULL(count(0),0) as count from opsmanage_project_order WHERE date_format(create_time,"%%Y%%m%%d") >= {startTime} and 
                        date_format(create_time,"%%Y%%m%%d") <= {endTime} and order_user='{user}'""".format(
                startTime=startTime, endTime=endTime, user=user)
            userData = Project_Order.objects.raw(sql)
            if userData[0].count == 0:
                data[user] = random.randint(1, 100)
            else:
                data[user] = userData[0].count
        monthDataList.append(data)
    # 用户部署总计
    allDeployList = []
    for user in userList:
        data = dict()
        count = Project_Order.objects.filter(order_user=user).count()
        data['user'] = user
        data['count'] = count
        allDeployList.append(data)
    # 获取资产更新日志
    assetsLog = Log_Assets.objects.all().order_by('-id')[0:10]
    # 获取所有项目数据
    assets = Assets.objects.all().count()
    project = Project_Config.objects.all().count()
    cron = Cron_Config.objects.all().count()
    playbook = Ansible_Playbook.objects.all().count()
    projectTotal = {
        'assets': assets,
        'project': project,
        'playbook': playbook,
        'cron': cron
    }
    return render_to_response('dashboard.html', {"user": request.user, "orderList": dataList,
                                                 "userList": userList, "dateList": dateList,
                                                 "monthDataList": monthDataList, "monthList": monthList,
                                                 "allDeployList": allDeployList, "assetsLog": assetsLog,
                                                 "orderNotice": orderNotice, "projectTotal": projectTotal},
                              context_instance=RequestContext(request))


@login_required(login_url='/login')
@permission_required('OpsManage.can_change_global_config', login_url='/noperm/')
def config(request):
    if request.method == "GET":
        try:
            config = Global_Config.objects.get(id=1)
        except:
            config = None
        try:
            email = Email_Config.objects.get(id=1)
        except:
            email = None
        return render_to_response('config.html', {"user": request.user, "config": config,
                                                  "email": email},
                                  context_instance=RequestContext(request))
    elif request.method == "POST":
        if request.POST.get('op') == "log":
            try:
                count = Global_Config.objects.filter(id=1).count()
            except:
                count = 0
            if count > 0:
                Global_Config.objects.filter(id=1).update(
                    ansible_model=request.POST.get('ansible_model'),
                    ansible_playbook=request.POST.get('ansible_playbook'),
                    cron=request.POST.get('cron'),
                    project=request.POST.get('project'),
                    assets=request.POST.get('assets', 0),
                    server=request.POST.get('server', 0),
                    email=request.POST.get('email', 0),
                )
            else:
                config = Global_Config.objects.create(
                    ansible_model=request.POST.get('ansible_model'),
                    ansible_playbook=request.POST.get('ansible_playbook'),
                    cron=request.POST.get('cron'),
                    project=request.POST.get('project'),
                    assets=request.POST.get('assets'),
                    server=request.POST.get('server'),
                    email=request.POST.get('email')
                )
            return JsonResponse({'msg': '配置修改成功', "code": 200, 'data': []})
        elif request.POST.get('op') == "email":
            try:
                count = Email_Config.objects.filter(id=1).count()
            except:
                count = 0
            if count > 0:
                Email_Config.objects.filter(id=1).update(
                    site=request.POST.get('site'),
                    host=request.POST.get('host', None),
                    port=request.POST.get('port', None),
                    user=request.POST.get('user', None),
                    passwd=request.POST.get('passwd', None),
                    subject=request.POST.get('subject', None),
                    cc_user=request.POST.get('cc_user', None),
                )
            else:
                Email_Config.objects.create(
                    site=request.POST.get('site'),
                    host=request.POST.get('host', None),
                    port=request.POST.get('port', None),
                    user=request.POST.get('user', None),
                    passwd=request.POST.get('passwd', None),
                    subject=request.POST.get('subject', None),
                    cc_user=request.POST.get('cc_user', None),
                )
            return JsonResponse({'msg': '配置修改成功', "code": 200, 'data': []})


def create_code_img(request):
    # 在内存中开辟空间用以生成临时的图片
    f = BytesIO()
    # 创建图片，模式，大小，背景色
    img = Image.new('RGB', (120, 30), (255, 255, 255))
    # 创建画布
    draw = ImageDraw.Draw(img)
    # 设置字体
    font = ImageFont.truetype('Arial.ttf', 25)

    code = getRandomChar()
    # 将生成的字符画在画布上
    for t in range(4):
        draw.text((30 * t + 5, 0), code[t], getRandomColor(), font)

    # 生成干扰点
    for _ in range(random.randint(0, 150)):
        # 位置，颜色
        draw.point((random.randint(0, 120), random.randint(0, 30)), fill=getRandomColor())

    # 使用模糊滤镜使图片模糊
    # img = img.filter(ImageFilter.BLUR)

    request.session['check_code'] = code
    img.save(f, 'gif')
    return HttpResponse(f.getvalue(), 'image/gif')


# 生成随机字符串
def getRandomChar():
    # string模块包含各种字符串，以下为小写字母加数字
    ran = string.ascii_lowercase + string.digits
    char = ''
    for i in range(4):
        char += random.choice(ran)
    return char


# 返回一个随机的RGB颜色
def getRandomColor():
    return (random.randint(50, 150), random.randint(50, 150), random.randint(50, 150))
