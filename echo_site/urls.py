# -*- coding: UTF-8 -*-
"""echo_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

import echo.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^index/', echo.views.index,name= 'index'),

    #用户登陆列表
    #用户登陆
    url(r'login/', echo.views.login, name='login'),
    #用户退出
    url(r'logout/', echo.views.logout, name='logout'),
    #密码修改
    url(r'password_change/', echo.views.password_change, name='password_change'),

    #基础资料的显示
    #内容显示,并通过定义name，来进行反向解析
    url(r'^lists/(?P<table>\w+)/$', echo.views.lists, name='lists'),
    #增加内容
    url(r'^add/(?P<table>\w+)/$', echo.views.add, name='add'),
    #修改数据,?P<pk>\d+代表穿过来的id值，且id值一定为数字
    url(r'^edit/(?P<table>\w+)/(?P<pk>\d+)/$', echo.views.edit, name='edit'),
    #删除数据
    url(r'^delete/(?P<table>\w+)/(?P<pk>\d+)/$', echo.views.delete, name='delete'),


    #任务列表
    url(r'^task_list/', echo.views.task_list, name='task_list'),
    url(r'^task_add/', echo.views.task_add, name='task_add'),
    url(r'^task_edit/(?P<pk>\d+)/$', echo.views.task_edit, name='task_edit'),
    url(r'^task_delete/(?P<pk>\d+)/$', echo.views.task_delete, name='task_delete'),
    url(r'^task_finish/(?P<pk>\d+)/$',echo.views.task_finish, name='task_finish'),


    #实施步骤
    url(r'^process_edit/(?P<pk>\d+)/$', echo.views.process_edit, name='process_edit'),
    url(r'^process_delete/(?P<pk>\d+)/$',echo.views.process_delete, name='process_delete'),

    #上传附件
    url(r'^upload_file/(?P<pk>\d+)/$', echo.views.upload_file, name='upload_file'),



]

#在测试环境中，将
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)