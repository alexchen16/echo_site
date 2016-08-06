# -*- coding: UTF-8 -*-
from .models import Node,Line,Device,Task,Process,Upload
from forms import NodeForm,LineForm,DeviceForm,TaskForm, ProcessForm,UploadFileForm
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.db import IntegrityError
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from upload import handle_uploaded_file
import json

from django.contrib.auth import views



import time
# Create your views here.

#显示首页
def index(request):
    #获取相应信息
    node_number = Node.objects.count()
    line_number = Line.objects.count()
    device_number = Device.objects.count()
    task_number = Task.objects.count()
    #获取已结单的数量,用于计算任务完成率
    task_complete = Task.objects.filter(task_status='已结单').count()
    #用float可以保留小树，round保留小数点2位
    if task_number:
        task_complete_percent = round(float(task_complete)/task_number*100,2)
    else:
        task_complete_percent = 0
    #将相关参数传递给dashboard页面
    context = {
        'page_title': '信息汇总',
        'node_number': node_number,
        'line_number': line_number,
        'device_number': device_number,
        'task_number': task_number,
        'task_complete': task_complete,
        'task_complete_percent': task_complete_percent,
    }
    return render(request,'dashboard.html',context)


#显示各列表信息
def lists(request, table):
    #从根据不同的请求，来获取相应的数据,并跳转至相应页面
    if table == 'node':
        #将原先的data更名为raw_data
        raw_data = Node.objects.all()
        list_template = 'node_list.html'
        sub_title = '节点信息'
    if table == 'line':
        raw_data = Line.objects.all()
        list_template = 'line_list.html'
        sub_title = '线路信息'
    if table == 'device':
        raw_data = Device.objects.all()
        list_template = 'device_list.html'
        sub_title = '设备信息'

    #通过GET方法从提交的URL来获取相应参数
    if request.method == 'GET':
        #建立一个空的参数的字典
        kwargs = {}
        #建立一个空的查询语句
        query = ''
        #提交过来的GET值是一个迭代的键值对
        for key, value in request.GET.iteritems():
            #刨去其中的token和page选项
            if key != 'csrfmiddlewaretoken' and key != 'page':
                #由于线路和设备的外键均与node表格有关，当查询线路中的用户名称或设备信息中的使用部门时，可以直接通过以下方式跨表进行查找
                if key == 'node':
                    kwargs['node__node_name__contains'] = value
                    #该query用于页面分页跳转时，能附带现有的搜索条件
                    query += '&' + key + '=' + value
                #其余的选项均通过key来辨别
                else:
                    kwargs[key + '__contains'] = value
                    #该query用于页面分页跳转时，能附带现有的搜索条件
                    query += '&' + key + '=' + value
        #通过元始数据进行过滤，过滤条件为健对值的字典
        data = raw_data.filter(**kwargs)
    #如果没有从GET提交中获取信息，那么data则为元始数据
    else:
        data = raw_data

    #将分页的信息传递到展示页面中去
    data_list, page_range, count, page_nums = pagination(request, data)
    #建立context字典，将值传递到相应页面
    context = {
        'data': data_list,
        'table': table,
        'query': query,
        'page_range': page_range,
        'count': count,
        'page_nums': page_nums,
        'page_title': '基础资料',
        'sub_title': sub_title,
    }
    #跳转到相应页面，并将值传递过去
    return render(request,list_template,context)


#用于增加资源
def add(request, table):

    #根据提交的请求不同，获取来自不同Form的表单数据
    if table == 'node':
        form = NodeForm(request.POST or None)
        sub_title = '添加节点'
    if table == 'line':
        form = LineForm(request.POST or None)
        sub_title = '添加线路'
    if table == 'device':
        form = DeviceForm(request.POST or None)
        sub_title = '添加设备'
    #判断form是否有效
    if form.is_valid():
        #创建实例，需要做些数据处理，暂不做保存
        instance = form.save(commit=False)
        #将登录用户作为登记人
        if table == 'node':
            instance.node_signer = request.user
        if table == 'line':
            instance.line_signer = request.user
        if table == 'device':
            instance.device_signer = request.user
        #保存该实例
        instance.save()
        #跳转至列表页面,配合table参数，进行URL的反向解析
        return redirect('lists', table=table)

    #创建context来集中处理需要传递到页面的数据
    context = {
        'form': form,
        'table': table,
        'page_title': '基础资料',
        'sub_title': sub_title,
    }
    #如果没有有效提交，则仍留在原来页面
    return render(request, 'res_add.html',  context)

#修改数据,函数中的pk代表数据的id
def edit(request, table, pk):
    if table == 'line':
        #这是Django的一个快捷方法,通过pk去line表中取值，如果有值则返回，如果无值则抛出http404的异常
        #具体信息可参考https://docs.djangoproject.com/en/1.9/topics/http/shortcuts/
        table_ins = get_object_or_404(Line, pk=pk)
        #通过instance来将Form的数据做填充
        form = LineForm(request.POST or None, instance=table_ins)
        sub_title = '修改线路信息'
    if table == 'node':
        table_ins = get_object_or_404(Node, pk=pk)
        form = NodeForm(request.POST or None, instance=table_ins)
        sub_title = '修改机构信息'
    if table == 'device':
        table_ins = get_object_or_404(Device, pk=pk)
        form = DeviceForm(request.POST or None, instance=table_ins)
        sub_title = '修改设备信息'
    #判断form是否有效
    if form.is_valid():
        #创建实例，需要做些数据处理，暂不做保存
        instance = form.save(commit=False)
        #将登录用户作为登记人,在修改时，一定要使用str强制
        if table == 'node':
            instance.node_signer = str(request.user)
        if table == 'line':
            instance.line_signer = str(request.user)
        if table == 'device':
            instance.device_signer = str(request.user)
        #保存该实例
        instance.save()
        #跳转至列表页面,配合table参数，进行URL的反向解析
        return redirect('lists', table=table)

    context = {
        'table': table,
        'form': form,
        'page_title': '基础资料',
        'sub_title': sub_title,
    }
    #与res_add.html用同一个页面，只是edit会在res_add页面做数据填充
    return render(request, 'res_add.html', context)


#删除操作
def delete(request, table ,pk):
    #选择相应的表格
    if table == 'line':
        #通过id值获取相应表格的实例，有值则返回，无值则抛出异常
        table_ins = get_object_or_404(Line, pk=pk)

    if table == 'node':
        table_ins = get_object_or_404(Node, pk=pk)

    if table == 'device':
        table_ins = get_object_or_404(Device, pk=pk)

    #接收通过AJAX提交过来的POST
    if request.method == 'POST':
        #删除该条目
        try:
            table_ins.delete()
            #删除成功,则data信息为success
            data = 'success'
        except IntegrityError:
            #如因外键问题，或其他问题，删除失败，则报error
            data = 'error'
        #将最后的data值传递至JS页面，进行后续处理,safe是将对象序列化，否则会报TypeError错误
        return JsonResponse(data,safe=False)



#任务的列表显示
def task_list(request):
    #如果通过GET来获取了相应参数，那么进行查询
    if request.method == 'GET':
        #建立过滤条件的键值对
        kwargs = {}
        #默认显示处理中的任务
        kwargs['task_status'] = '处理中'
        #用于分页显示的query
        query = ''
        for key, value in request.GET.iteritems():
            #除去token及page的参数
            if key != 'csrfmiddlewaretoken' and key != 'page':
                #如果查询的是与处理过程相关的，那么需要通过外键跳转至process表格
                if key == 'process_content':
                    if value !='':
                        kwargs['process__process_content__contains'] = value
                elif key == 'process_signer':
                    if value !='':
                        kwargs['process__process_signer__contains'] = value
                #定义任务的开始与结束时间
                elif key == 'task_start':
                    if value != '':
                        kwargs['task_signtime__gte'] = value
                elif key == 'task_end':
                    if value != '':
                        kwargs['task_signtime__lte'] = value
                #定义任务的状态
                elif key == 'task_status':
                    if value == U'处理中':
                        kwargs['task_status'] = '处理中'
                    if value == U'已结单':
                        kwargs['task_status'] = '已结单'
                    #如果选择了所有状态，即对任务状态不进行过滤，那么就删除task_status这个键值对
                    if value == U'全部':
                        del kwargs['task_status']
                #其余的则根据提交过来的键值对进行过滤
                else:
                    kwargs[key + '__contains'] = value
                #建立用于分页的query
                query += '&' + key + '=' + value
        #按照登记时间排序
        data = Task.objects.filter(**kwargs).order_by('task_signtime')


    #如果没有GET提交过来的搜索条件，那么默认按照登记时间排序，并只显示处理中的任务
    else:
        data = Task.objects.filter(task_status='处理中').order_by('task_signtime')

    #进行分页
    data_list, page_range, count, page_nums = pagination(request, data)
    #构建context字典
    context = {
        'data': data_list,
        'page_range': page_range,
        'query': query,
        'count': count,
        'page_nums': page_nums,
        'page_title': '任务处理',
        'sub_title': '任务列表',
    }
    return render(request,'task_list.html',context)

#任务列表的相关处理函数

#任务列表的增加
def task_add(request):
    #从TaskForm获取相关信息
    form = TaskForm(request.POST or None)
    if form.is_valid():
        #建立一个task实例
        task_ins = Task()
        #通过时间来建立一个任务流水
        task_ins.task_code = str(int(time.time()))
        #获取task的相关信息
        task_ins.task_title = form.cleaned_data.get('task_title')
        task_ins.task_category = form.cleaned_data.get('task_category')
        task_ins.task_contacts = form.cleaned_data.get('task_contacts')
        #task建立后默认变成处理中的状态
        task_ins.task_status = '处理中'
        #通过登录用户来辨别任务登记人
        task_ins.task_signer = request.user
        #保存task实例
        task_ins.save()
        #通过当前task_id获取task对象，并将其赋给member_task
        member_task = Task.objects.get(id = task_ins.id)
        #获取members集合
        members = form.cleaned_data.get('task_member')
        #获取members集合中的member,并将其添加到member_task中,增添相应实施人员
        for member in members:
            member_task.task_member.add(member)

        #通过task_id获取task对象
        process_task = Task.objects.get(id = task_ins.id)
        #建立一个process的实施步骤实例
        process_ins = Process()
        #将process实例与task绑定
        process_ins.task = process_task
        #获取process相关信息
        process_ins.process_content = form.cleaned_data.get('process_content')
        process_ins.process_signer = request.user
        process_ins.save()


        return redirect('task_list')

    context = {
        'form': form,
        'page_title': '任务处理',
        'sub_title': '新建任务',
    }
    return render(request, 'task_add.html',  context)

#任务的编辑
def task_edit(request, pk):
    #获取相关任务实例
    task_ins = get_object_or_404(Task, pk=pk)
    #如果收到了相应的POST提交
    if request.method == 'POST':
        #任务联系人为可编辑选项，并填充原先的任务联系人
        task_ins.task_contacts = request.POST['task_contacts']
        task_ins.save()

        #通过所在task_id获取task对象
        process_task = Task.objects.get(id = task_ins.id)
        #如果获取的实施步骤内容不为空,建立process对象，并增加相关信息
        if request.POST['process_content'].strip(' ') != '':
            process_ins = Process()
            process_ins.task = process_task
            process_ins.process_content = request.POST['process_content'].strip(' ')
            process_ins.process_signer = request.user
            process_ins.save()

        return redirect('task_edit', pk=task_ins.id)

    context = {
        'task': task_ins,
        'user': str(request.user),
        'page_title': '任务处理',
        'sub_title': '编辑任务',
    }
    return render(request, 'task_edit.html', context)

#任务列表的任务删除
def task_delete(request, pk):
    #获取选定的task实例
    task_ins = get_object_or_404(Task, pk=pk)
    #如果接收到了删除的POST提交，则删除相应条目
    if request.method == 'POST':
        try:
            task_ins.delete()
            #删除成功,则data信息为success
            data = 'success'
        except IntegrityError:
            #如因外键问题，或其他问题，删除失败，则报error
            data = 'error'
        #将最后的data值传递至JS页面，进行后续处理,safe是将对象序列化，否则会报TypeError错误
        return JsonResponse(data, safe=False)

#结束任务功能
def task_finish(request, pk):
    #获取任务实例
    task_ins = get_object_or_404(Task,pk=pk)
    #获得该提交
    if request.method == 'POST':
        try:
            #将task的状态置为已结单
            task_ins.task_status = '已结单'
            task_ins.save()
            #在process增加一条记录，标识某人结束了该项任务
            process_task = Task.objects.get(id = task_ins.id)
            process_ins = Process()
            process_ins.task = process_task
            process_ins.process_content = str(request.user) + u'完成了该项任务并结单'
            process_ins.process_signer = request.user
            process_ins.save()
            #返回JSON值,success
            data = 'success'
        except IntegrityError:
            #返回JSON值,error
            data = 'error'
        #通过json形式返回相关数值
        return HttpResponse(json.dumps(data), content_type = "application/json")

#实施步骤的修改
def process_edit(request, pk):
    #获取相应的实施步骤
    process_ins = get_object_or_404(Process, pk=pk)
    #如果收到了POST提交
    if request.method == 'POST':
        #调用process的form
        form = ProcessForm(request.POST)
        if form.is_valid():
            process_ins.process_content = request.POST['process_content'].strip(' ')
            process_ins.process_signtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            process_ins.save()

            return redirect('task_edit', pk=process_ins.task_id)
    #将之前的process内容放入processform
    form = ProcessForm(initial={'process_content': process_ins.process_content})

    #将相应的context值传递到实施步骤修改页面
    context = {
        'id': process_ins.task_id,
        'form': form,
        'page_title': '任务处理',
        'sub_title': '编辑任务',

    }

    return render(request, 'process_edit.html', context)

#实施步骤删除
def process_delete(request, pk):
    #获取相应的实施步骤
    process_ins = get_object_or_404(Process, pk=pk)
    #如果接收到了POST的提交
    if request.method == 'POST':
        try:
            process_ins.delete()
            #删除成功,则data信息为success
            data = 'success'
        except IntegrityError:
            #如因外键问题，或其他问题，删除失败，则报error
            data = 'error'
        #将最后的data值传递至JS页面，进行后续处理,safe是将对象序列化，否则会报TypeError错误
        return JsonResponse(data, safe=False)

#上传附件函数
def upload_file(request, pk):
    #获得一个任务的实例
    task_ins = get_object_or_404(Task, pk=pk)

    #如果获取到了POST的提交
    if request.method == 'POST':
        #获取form表单，request.FILES是存放文件的地方
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            #通过处理上传文件函数来获得返回值
            uf = handle_uploaded_file(request.FILES['file'])

            #获取上传文件的实例，并补充相应信息至数据库中
            upload_ins = Upload()
            #绑定相应的task id
            upload_ins.task_id = task_ins.id
            #记录相应的文件名
            upload_ins.upload_title = uf[0]
            #记录相应的上传路径
            upload_ins.upload_path = uf[1]
            #保存upload的实例
            upload_ins.save()
            return redirect('task_edit', pk=task_ins.id)
    else:
        form = UploadFileForm()

    #构建相应的context，传递至上传文件页面
    context = {
        'form': form,
        'page_title': '任务处理',
        'sub_title': '上传文件',

    }
    return render(request, 'upload.html', context)




#分页函数
def pagination(request, queryset, display_amount=2, after_range_num = 5,before_range_num = 4):
    #按参数分页

    try:
        #从提交来的页面获得page的值
        page = int(request.GET.get("page", 1))
        #如果page值小于1，那么默认为第一页
        if page < 1:
            page = 1
    #若报异常，则page为第一页
    except ValueError:
            page = 1
    #引用Paginator类
    paginator = Paginator(queryset, display_amount)
    #总计的数据条目
    count = paginator.count
    #合计页数
    num_pages = paginator.num_pages



    try:
        #尝试获得分页列表
        objects = paginator.page(page)
    #如果页数不存在
    except EmptyPage:
        #获得最后一页
        objects = paginator.page(paginator.num_pages)
    #如果不是一个整数
    except PageNotAnInteger:
        #获得第一页
        objects = paginator.page(1)
    #根据参数配置导航显示范围
    temp_range = paginator.page_range

    #如果页面很小
    if (page - before_range_num) <= 0:
        #如果总页面比after_range_num大，那么显示到after_range_num
        if temp_range[-1] > after_range_num:
            page_range = xrange(1, after_range_num+1)
        #否则显示当前页
        else:
            page_range = xrange(1, temp_range[-1]+1)
    #如果页面比较大
    elif (page + after_range_num) > temp_range[-1]:
        #显示到最大页
        page_range = xrange(page-before_range_num,temp_range[-1]+1)
    #否则在before_range_num和after_range_num之间显示
    else:
        page_range = xrange(page-before_range_num+1, page+after_range_num)
    #返回分页相关参数
    return objects, page_range, count, num_pages

#用户登陆选项，所有的函数将会返回一个template_response的实例，用来描绘页面，同时你也可以在return之前增加一些特定的功能
#用户登陆
def login(request):
    #extra_context是一个字典，它将作为context传递给template，这里告诉template成功后跳转的页面将是/index
    template_response = views.login(request, extra_context={'next': '/index/'})
    return template_response

#用户退出
def logout(request):
    #logout_then_login表示退出即跳转至登陆页面，login_url为登陆页面的url地址
    template_response = views.logout_then_login(request,login_url='/login/')
    return template_response

#密码更改
def password_change(request):
    #post_change_redirect表示密码成功修改后将跳转的页面.
    template_response = views.password_change(request,post_change_redirect='/index/')
    return template_response