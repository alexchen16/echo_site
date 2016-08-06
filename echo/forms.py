# -*- coding: UTF-8 -*-
from django.forms import ModelForm
from django import forms
from .models import Node,Line,Device,Employee

#定义Node的Form,Form名字为 模式名+Form
class NodeForm(ModelForm):
    #自定义ModelForm的内容
    class Meta:
        #该ModelForm参照Model: Node
        model = Node
        #在Form中不显示node_signer这个字段
        exclude = ['node_signer']

class LineForm(ModelForm):
    class Meta:
        model = Line
        exclude = ['line_signer']

class DeviceForm(ModelForm):
    class Meta:
        model = Device
        exclude = ['device_signer']


#定义TaskForm，但不根据ModelForm来定义
class TaskForm(forms.Form):
    #任务类型的分类
    category = (
        (U'综合事务','综合事务'),
        (U'机构建设','机构建设'),
        (U'线路事务','线路事务'),

    )
    task_title = forms.CharField(label = '任务名称',max_length = 255)
    task_category = forms.ChoiceField(label='任务分类',choices= category)
    #建立联系人，其中的textarea做了规格设定，默认行高为2
    task_contacts = forms.CharField(label = '联系人',widget=forms.Textarea(attrs={'rows': '2'}),required=False)
    #建立一个复选框的实施人员，通过queryset来获取人员列表
    task_member = forms.ModelMultipleChoiceField(label='实施人员',
                                                 queryset=Employee.objects.all(),
                                                 widget=forms.CheckboxSelectMultiple)
    #建立一个处理过程
    process_content = forms.CharField(label = '处理过程',widget=forms.Textarea)


#建立实施步骤的表单
class ProcessForm(forms.Form):
    process_content = forms.CharField(label = '处理过程',widget=forms.Textarea)


#建立上传附件的FORM
class UploadFileForm(forms.Form):
    #提供一个上传附件的FORM
    file = forms.FileField()