# -*- coding: UTF-8 -*-
#迁移时，能使python2的语法运用在python3上
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
#建立职员模型，这是对内置user表的扩展
class Employee(models.Model):
    #对应User表，建立一对一的模型，目的是更好地扩展而不影响原user表结构
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #定义user的职责
    responsibility = models.CharField(max_length=100,blank=True)

    def __unicode__(self):
        return self.user.username



#建立节点信息表
class Node(models.Model):

    #线路的类型选择，作为node_type的选项
    type = (
        (U'总部','总部'),
        (U'分部','分部'),
    )
    #verbose_name可以让admin后台显示自定义的中文名字，而非字段
    node_name = models.CharField(verbose_name='节点名称',max_length=255)
    #choices找到type元组，并调用相关内容
    node_type = models.CharField(verbose_name='节点类型',max_length=50,choices=type)
    node_address = models.CharField(verbose_name='节点地址',max_length=255)
    #blank为空，代表在form中可以允许不填
    node_contact = models.CharField(verbose_name='节点联系人',max_length=255,blank=True)
    #default表示默认值
    node_signer = models.CharField(verbose_name='登记人',max_length=50, default='system')
    node_remarks = models.CharField(verbose_name='备注',max_length=255,blank=True)
    #登记时间设置为自动记录，不会出现在选项中
    node_signtime = models.DateField(auto_now_add= True)

    #返回相应的值
    def __unicode__(self):
        return self.node_name


#建立线路信息表
class Line(models.Model):

    #与node形成一对多的关系，在删除node的同时，如果有线路信息依附在该节点上，那么删除失败
    node = models.ForeignKey(Node,on_delete=models.PROTECT)

    #运营商分类
    spname = (
        (u'中国电信','中国电信'),
        (u'中国联通','中国联通'),
        (u'中国移动','中国移动'),
        (u'中国铁通','中国铁通'),
        (u'其他','其他')
    )
    #线路速率
    speed = (
        ('2M','2M'),
        ('4M','4M'),
        ('6M','6M'),
        ('10M','10M'),
        (u'其他','其他'),
    )
    #线路类型
    type = (
        ('MSTP','MSTP'),
        ('MSAP','MASP'),
        ('SDH','SDH'),
        ('DIAL','DIAL'),
        (u'其他','其他'),
    )

    line_code = models.CharField(verbose_name='线路编号',max_length=100)
    line_local = models.CharField(verbose_name='所在机房',max_length=50,default='上海数据中心')
    line_speed = models.CharField(verbose_name='线路速率',max_length=10,choices=speed,default='6M')
    line_spname = models.CharField(verbose_name='运营商',max_length=10,choices=spname,default='信网公司')
    line_type = models.CharField(verbose_name='线路类型',max_length=50,choices=type,default='MSTP')
    line_status = models.BooleanField(verbose_name='线路启用',default=True)
    line_open = models.DateField(verbose_name='开通时间')
    line_closed = models.DateField(verbose_name='关闭时间',blank=True,null=True)
    line_signer = models.CharField(verbose_name='登记人',max_length=30,default='system')
    line_signtime = models.DateField(auto_now_add=True)
    line_remarks = models.CharField(verbose_name='备注',max_length=255,blank=True)

    def __unicode__(self):
        return self.line_code

#建立设备信息表
class Device(models.Model):

    node = models.ForeignKey(Node, on_delete=models.PROTECT)

    vendor = (
        ('CISCO', 'CISCO'),
        ('JUNIPER','JUNIPER'),
        ('TOPSEC','TOPSEC'),
        ('HUAWEI','HUAWEI'),
        ('H3C','H3C'),
    )

    device_caption = models.CharField(verbose_name='设备名称',max_length=100)
    device_serial = models.CharField(verbose_name='设备序列号',max_length=100)
    device_type = models.CharField(verbose_name='设备型号',max_length=50)
    device_vendor = models.CharField(verbose_name='设备厂商',max_length=50,choices=vendor)
    device_remark = models.CharField(verbose_name='备注',max_length=50,blank=True)
    device_ip = models.GenericIPAddressField(verbose_name='管理IP')
    device_status = models.CharField(verbose_name='设备状态',max_length=10,default='启用')
    device_signer = models.CharField(verbose_name='登记人',max_length=30,default='system')
    device_signtime = models.DateField(auto_now_add=True)


    def __unicode__(self):
        return self.device_caption

#建立任务表
class Task(models.Model):
    #执行的任务和人员关系是多对多的关系
    task_member = models.ManyToManyField(Employee)
    #为任务类型分类
    category = (
        (U'综合事务','综合事务'),
        (U'机构建设','机构建设'),
        (U'线路事务','线路事务'),
    )
    #任务的流水号
    task_code = models.CharField(max_length=30, default='error_code')
    #任务的名称
    task_title = models.CharField(verbose_name='任务名称',max_length=100)
    #任务的分类
    task_category = models.CharField(verbose_name='任务分类',max_length=100,choices=category,default='综合事务')
    #任务的联系人
    task_contacts = models.TextField(verbose_name='联系人',blank=True)
    #任务状态
    task_status = models.CharField(verbose_name='处理中',max_length=20,default='处理中')
    #任务登记人
    task_signer = models.CharField(max_length=30,default='system')
    #任务登记时间
    task_signtime = models.DateField(auto_now_add=True)

    def __unicode__(self):
        return self.task_title

#建立实施步骤
class Process(models.Model):
    #与task表格是一对多的关系，依附于task之上
    task = models.ForeignKey(Task)
    #实施步骤内容
    process_content = models.TextField(blank=True)
    #实施步骤登记时间
    process_signtime = models.DateTimeField(auto_now_add=True)
    #实施步骤登记人
    process_signer = models.CharField(max_length=30,default='system')

    def __unicode__(self):
        return self.process_content

#上传附件
class Upload(models.Model):
    #与task表格是一对多的关系，依附于task之上
    task = models.ForeignKey(Task)
    #上传附件名称
    upload_title = models.CharField(max_length=255)
    #上传附件路径
    upload_path = models.CharField(max_length=255)
    #上传附件时间
    upload_signtime = models.DateTimeField(auto_now_add=True,null=True)

    def __unicode__(self):
        return self.upload_title
