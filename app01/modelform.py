from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile 
from app01 import models
from django.shortcuts import render,HttpResponse,redirect
from .jiami import *
import arrow 
import django_filters

today = arrow.now().format('YYYY-MM-DD HH:mm:ss')
date= arrow.now().shift(days=0).format('YYYY-MM-DD')





class WeighingRecordForm(forms.ModelForm):
    class Meta:
        model =models.WeighingRecord
        exclude = ['created_at']  # 自动生成的时间字段无需填写
        labels = {
            'weight_number': '磅单号',
            'truck_driver': '大车司机',
            'forklift_driver': '铲车司机', 
            'net_weight': '矿石净重',
            'weight_photo': '称重单照片'
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 为所有字段添加 Bootstrap 样式
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
        # 特殊处理图片字段
        self.fields['weight_photo'].widget = forms.ClearableFileInput(attrs={
            'class': 'form-control-file',
            'accept': 'image/*'
        })


class Login(forms.Form):
    ident=forms.CharField( label='账号',
        widget=forms.TextInput)

    password=forms.CharField(
        label='密码',
        error_messages={'required': '密码不能为空'},
        widget=forms.PasswordInput )
    
    def clean_password(self):
        pwd=self.cleaned_data.get('password')
        return md5(pwd)
    
    def __init__(self, *args, **kwargs):
        super(Login, self).__init__(*args, **kwargs)
        for name,field in self.fields.items():
            field.widget.attrs={'class': 'form-control'}









class Ti(forms.ModelForm):
    class Meta:
        model = models.Tihao
        fields = []# 以列表的形式写入字段


    ti=[v['题号'] for i,v in enumerate(models.Tihao.objects.values('题号'))]
    id=locals()
    choice=[(v,v) for i,v in enumerate(list('ABCDE对错'))]
    
    for i in ti:
        
        id[str(i)] =forms.MultipleChoiceField(choices=choice,required=False,label=str(i),widget=forms.CheckboxSelectMultiple(),)# widget=forms.CheckboxSelectMultiple,
     


    date =forms.DateField(required=True,initial=arrow.now().shift(days=0).format('YYYY-MM-DD'),
                        error_messages={'required': '由于计划不能为空'}
                        ,widget=forms.DateInput(format='%Y-%m-%d',attrs={'type': 'date'}),label="日期")
    # def __init__(self, *args, **kwargs) :
    #     super().__init__(*args,**kwargs)
    #     for name,field in self.fields.items():
    #         # field.widget.attrs={'class': 'form-check-input'}






class Ti1(forms.ModelForm):
    class Meta:
        model = models.Tihao
        fields = []# 以列表的形式写入字段


    ti = [v['题号'] for v in models.Tihao.objects.values('题号') if '多选' not in str(v['题号'])]
    id=locals()
    choice=[(v,v) for i,v in enumerate(list('ABCDE对错'))]
    
    for i in ti:
        
        id[str(i)] =forms.MultipleChoiceField(choices=choice,required=False,label=str(i),widget=forms.CheckboxSelectMultiple(),)# widget=forms.CheckboxSelectMultiple,
     

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 动态设置日期初始值
        self.fields['date'].initial = arrow.now().format('YYYY-MM-DD')

    date = forms.DateField(
        required=True,
        error_messages={'required': '由于计划不能为空'},
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={'type': 'date'}
        ),
        label="日期"
    )






























class StaffFilter(django_filters.FilterSet):
    class Meta:
        model = models.Admin
        fields = ['username', 'role','department']  # 可筛选的字段





class Staff(forms.ModelForm):
    username = forms.CharField(label='姓名')
    department = forms.CharField(label='部门')
        # 新增照片上传字段
    avatar = forms.ImageField(
        label="管理员头像",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'form-control',  # 保留原有样式
                'accept': 'image/*'       # 新增类型限制
            }
        )
    )
    class Meta:
        model = models.Admin
        fields = "__all__"# 以列表的形式写入字段
        exclude=["id"] 
    password=forms.CharField(required=True,widget=forms.PasswordInput(render_value=True),label="密码")
    password_ =forms.CharField(required=True,widget=forms.PasswordInput(render_value=True),label="再次输入")  
    # 照片=forms.FileField(label="照片")  
    def clean_password(self):
        pwd=self.cleaned_data.get('password')
        
        return md5(pwd)


    def clean_password_(self):
        
        pwd=self.cleaned_data.get('password')
        pwd_=self.cleaned_data.get('password_')
        print(md5(pwd))
        if pwd!=md5(pwd_):            
            raise ValidationError("输入不一错误")        
        return pwd_    
    #ident =forms.CharField(disabled=True,initial='ident1')
    
    
    def clean(self):
        cleaned_data = super().clean()
        for field_name, field in self.fields.items():
            # 跳过允许为空的字段
            if field.required and not cleaned_data.get(field_name):
                self.add_error(field_name, "该字段不能为空")
        return cleaned_data


        # 新增文件大小验证（可选）
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if isinstance(avatar, InMemoryUploadedFile):
            if avatar.size > 20*1024*1024:
                raise ValidationError("头像文件大小不能超过20MB")
            # 新增返回验证通过的文件
            return avatar
        return avatar  # 修改这里保持已有文件不变










class CategoryContentForm(forms.ModelForm):
    class Meta:
        model =models.CategoryContent
        fields = '__all__'
    
    
    
    
    
       
    
    
    
    
    
    



class ExplosiveInventoryItemForm(forms.ModelForm):
    class Meta:
        model = models.ExplosiveInventoryItem
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 定义一个列表，包含需要排除的字段名
        exclude_fields = [
            
            'inventory_order_number',
            'emulsion_explosive_32mm', 'powdery_explosive_box_2', 'sticky_explosive', 'electronic_detonator_5m', 'electronic_detonator_15m',
            'detonator_code',
            'inventory_status',
            'explosive_quantity_90mm',
            'explosive_quantity_32mm',
            'detonating_device_quantity',
            'detonating_cord_length',
            'date'
            
        ]
        
        
        
        
        
        for field_name, field in self.fields.items():
            if field_name not in exclude_fields:
                # 使用自定义的 ContentChoiceField 替换需要显示 content 字段的字段
                choice=[(v['content'],v['content']) for i,v in enumerate(models.CategoryContent.objects.values('category','content')) if v['category']==field_name]#field_name
                
                choice=list(set(choice)) 
                choice.sort()
                
         
                
                
                self.fields[field_name] = forms.ChoiceField(choices=choice)

                # 设置字段的标签为模型字段的 verbose_name
                self.fields[field_name].label = self.Meta.model._meta.get_field(field_name).verbose_name
                self.fields['date'].initial = arrow.now().format('YYYY-MM-DD')





  

# ... 文件头部已有导入和代码保持不变 ...

class CandidateProfileForm(forms.ModelForm):
    class Meta:
        model = models.Candidate
        fields = '__all__'
        exclude = ['created_at','resume_file']  # 自动生成的字段不需要在表单中显示
        widgets = {
            'birthday': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
            'photo': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                    'accept': 'image/*'
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 为所有字段添加bootstrap样式
        for field_name, field in self.fields.items():
            if field_name not in ['photo', 'birthday']:  # 已经单独设置样式的字段跳过
                field.widget.attrs.update({'class': 'form-control'})
            # 设置日期字段初始值
            if field_name == 'birthday':
                field.initial = arrow.now().format('YYYY-MM-DD')

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name.strip()) < 2:
            raise ValidationError("姓名至少需要2个字符")
        return name.strip()

# ... 文件其他部分保持不变 ...























# class Admin(forms.ModelForm):

#     class Meta:

#         model = Admin
#         fields = "__all__"# 以列表的形式写入字段
#         exclude=["id"] 
#     password=forms.CharField(required=True,widget=forms.PasswordInput(render_value=True),label="密码")
#     password_ =forms.CharField(required=True,widget=forms.PasswordInput(render_value=True),label="再次输入")  
#     照片=forms.FileField(label="照片")  
#     def clean_password(self):
#         pwd=self.cleaned_data.get('password')
        
#         return md5(pwd)


#     def clean_password_(self):
        
#         pwd=self.cleaned_data.get('password')
#         pwd_=self.cleaned_data.get('password_')
#         print(md5(pwd))
#         if pwd!=md5(pwd_):            
#             raise ValidationError("输入不一错误")        
#         return pwd_    
#     ident =forms.CharField(disabled=True,initial='ident1')
    
#     def clean_ident(self):        
#         pwd=self.cleaned_data.get('ident')
#         print(self.instance.id,'-------')
#         exists=Admin.objects.exclude(id=self.instance.id).filter(ident=str(pwd)).exists()
#         if exists:            
#             raise ValidationError("ident号已存在")
#         if len(pwd)!=6:            
#             raise ValidationError("ident号六位数字")        
#         return pwd 
    
#     def __init__(self, *args, **kwargs) :
#         super().__init__(*args,**kwargs)
#         for name,field in self.fields.items():
#             field.widget.attrs={'class': 'form-control'}    


# class City(forms.ModelForm):

#     class Meta:

#         model = City
#         fields = "__all__"# 以列表的形式写入字段
      
 
# class Sportlist_select(forms.ModelForm):    
#     ident =forms.CharField(disabled=True,initial='ident')#,initial=clean_ident()
#     开始日期 =forms.DateField(disabled=False,required=True,widget=forms.DateInput(attrs={'type': 'date'} ))
#     结束日期 =forms.DateField(disabled=False,required=True,initial=arrow.now().shift(days=0).format('YYYY-MM-DD'),widget=forms.DateInput(attrs={'type': 'date'} ))
#     class Meta:
#         model = models.Sportlist
#         fields = ['ident','content']
#     choice=[(v['content'],v['content']) for i,v in enumerate(models.Sportlist.objects.values('content'))]
#     choice=list(set(choice))
#     choice.append(('','全选'))
#     content=forms.ChoiceField(required=False,choices=choice,label='content')

#     def clean_结束日期(self):       
#         txt_结束日期=self.cleaned_data['结束日期']
#         print(txt_结束日期,'---------')
#         if txt_结束日期=='':
#             raise ValidationError("格式错误")
#         return txt_结束日期
    
#     def clean_开始日期(self):
#         txt_开始日期=self.cleaned_data['开始日期']
   
#         if txt_开始日期=='':
#             raise ValidationError("必须填写")
#         return txt_开始日期

#     def __init__(self, *args, **kwargs):

#         self.request = kwargs.pop('request', None)
#         super(Sportlist_select, self).__init__(*args, **kwargs)
        

#         for name,field in self.fields.items():
#             field.widget.attrs={'class': 'form-control'}
#             if name=='结束日期':
#                 field.initial=arrow.now().shift(days=1).format('YYYY-MM-DD')
#                 field.required=True
#             if name=='开始日期':
#                 field.initial=arrow.now().shift(days=-365).format('YYYY-MM-DD')
#                 field.required=True

# class Sportlist(forms.ModelForm):    
#     ident =forms.CharField(disabled=True)#,initial=clean_ident()
#     日期 =forms.DateTimeField(disabled=False,widget=forms.DateTimeInput(format='%Y-%m-%d %H:%M',
#                                                          attrs={'type': 'datetime-local'}))
#     class Meta:
#         model = models.Sportlist
#         fields = ['ident','日期','content','重量','次数','组数']
#         # exclude=['ident']

#     choice=[(v['content'],v['content']) for i,v in enumerate(models.Sportlist.objects.values('content'))]
#     choice=list(set(choice))
#     # choice.append(('','全选'))
#     content=forms.ChoiceField(choices=choice,label='content')

#     def __init__(self, *args, **kwargs):
#         super(Sportlist, self).__init__(*args, **kwargs)

#         for name,field in self.fields.items():
#             field.widget.attrs={'class': 'form-control'}
#             if name=='ident':
#                 field.initial='ident'
#             if name=='日期':
#                 field.initial=arrow.now().format('YYYY-MM-DD HH:mm:ss') 

# class Answer(forms.Form):    
#     第一个数字 =forms.IntegerField()#,initial=clean_ident()IntegerField方法代码示例 - 纯净天空
#     第二个数字 =forms.IntegerField()
#     第三个数字 =forms.IntegerField()
#     第四个数字 =forms.IntegerField()


#     def __init__(self, *args, **kwargs):
#         super(Answer, self).__init__(*args, **kwargs)
#         for name,field in self.fields.items():
#             field.widget.attrs={'class': 'form-control'}


# # class Mp3(forms.ModelForm):    
# #     ident =forms.CharField(disabled=True)#,initial=clean_ident()
# #     日期 =forms.DateTimeField(initial=today,widget=forms.DateTimeInput(format='%Y-%m-%d %H:%M',
# #                                                          attrs={'type': 'datetime-local'}))


# #     class Meta:

# #         model = models.Mp3
#         fields = "__all__"




#     def __init__(self, *args, **kwargs):
#         super(Mp3, self).__init__(*args, **kwargs)

#         for name,field in self.fields.items():
#             field.widget.attrs={'class': 'form-control'}
#             if name=='ident':
#                 field.initial='ident'

# class Mp3_select(forms.ModelForm):    

    
#     ident =forms.CharField(disabled=True,initial='ident')#,initial=clean_ident()
#     开始日期 =forms.DateTimeField(disabled=False,required=True,widget=forms.DateInput(attrs={'type': 'date'} ))
#     结束日期 =forms.DateField(disabled=False,required=True,initial=arrow.now().shift(days=0).format('YYYY-MM-DD'),widget=forms.DateInput(attrs={'type': 'date'} ))
#     class Meta:

#         model = models.Mp3
#         exclude=['mp3','日期','文件名']

#     def clean_结束日期(self):
       
#         txt_结束日期=self.cleaned_data['结束日期']
#         print(txt_结束日期,'---------')
#         if txt_结束日期=='':
#             raise ValidationError("格式错误")
#         return txt_结束日期
    
#     def clean_开始日期(self):
#         txt_开始日期=self.cleaned_data['开始日期']
   
#         if txt_开始日期=='':
#             raise ValidationError("必须填写")
#         return txt_开始日期

#     def __init__(self, *args, **kwargs):

#         self.request = kwargs.pop('request', None)
#         super(Mp3_select, self).__init__(*args, **kwargs)
        

#         for name,field in self.fields.items():
#             field.widget.attrs={'class': 'form-control'}
#             if name=='结束日期':
#                 field.initial=arrow.now().shift(days=0).format('YYYY-MM-DD')
#                 field.required=True
#             if name=='开始日期':

#                 field.required=True

# class Safe_select(forms.ModelForm):    


#     class Meta:    

#         model = models.Safe
#         exclude=['值','因素','细分']
#     choice=[(v['项目'],v['项目']) for i,v in enumerate(models.Safe.objects.values('项目'))]
#     choice=list(set(choice))
#     choice.append(('','全选'))
#     项目=forms.ChoiceField(choices=choice,label='项目')


#     def __init__(self, *args, **kwargs):

#         self.request = kwargs.pop('request', None)
#         super(Safe_select, self).__init__(*args, **kwargs)
#         for name,field in self.fields.items():
#             field.widget.attrs={'class': 'form-control'}


# class HR(forms.ModelForm):
#     class Meta:
#         model = FHr
#         fields = ['id','ident','日期','content','重量','间隔时间','心率']# 以列表的形式写入字段


#     def __init__(self, *args, **kwargs) :
#         super().__init__(*args,**kwargs)
#         for name,field in self.fields.items():
#             field.widget.attrs={'class': 'form-control'}
#             if name=='日期':
#                 field.initial=arrow.now().format('YYYY-MM-DD HH:mm:ss')

#     ident =forms.CharField(disabled=True,initial='ident')

#     日期 =forms.DateField(required=True,initial=arrow.now().shift(days=0).format('YYYY-MM-DD'),widget=forms.DateInput(format='%Y-%m-%d',
#                                                          attrs={'type': 'date'}),label="日期")

#     choice=[(v['content'],v['content']) for i,v in enumerate(models.Sportlist.objects.values('content'))]
#     choice=list(set(choice))
#     content=forms.ChoiceField(choices=choice,label='content')
#     # my_field = forms.MultipleChoiceField(choices=choice, widget=forms.CheckboxSelectMultiple)
#     # question1 = forms.ChoiceField(choices=choice, widget=forms.RadioSelect)
#     choice=[(v,v) for i,v in enumerate(["2","3","4","5"])]
#     间隔时间=forms.ChoiceField(choices=choice,label='间隔时间(分钟)')

 
 

# class HR_select(forms.ModelForm):
    
#     class Meta:
#         model = FHr
#         fields = ['日期','content']# 以列表的形式写入字段


#     def __init__(self, *args, **kwargs) :
#         super().__init__(*args,**kwargs)
#         for name,field in self.fields.items():
#             field.widget.attrs={'class': 'form-control'}
#     choice=[(v['content'],v['content']) for i,v in enumerate(models.FHr.objects.values('content'))]
#     choice=list(set(choice))
#     content=forms.ChoiceField(choices=choice,label='content')
    



# # class Links_select(forms.ModelForm):   
# #     class Meta:
# #         model = models.Links
# #         fields=['source']
# #     # choice=[(v['source'],v['source']) for i,v in enumerate(models.Links.objects.values('source'))]
# #     # choice=list(set(choice))
# #     # choice.append(('','全选'))
# #     # 源=forms.ChoiceField(choices=choice,label='源')

# #     choice=[(v['categories'],v['categories']) for i,v in enumerate(models.Links.objects.values('categories'))]
# #     choice=list(set(choice))
# #     choice.append(('','全选'))
# #     分类=forms.ChoiceField(choices=choice,label='分类')


# #     def __init__(self, *args, **kwargs):

# #         self.request = kwargs.pop('request', None)
# #         super().__init__(*args, **kwargs)
# #         for name,field in self.fields.items():
# #             field.widget.attrs={'class': 'form-control'}
        

# class Run_select(forms.ModelForm):    
#     ident =forms.CharField(disabled=True,initial='ident')#,initial=clean_ident()
#     开始日期 =forms.DateTimeField(disabled=False,required=True,widget=forms.DateInput(attrs={'type': 'date'} ))
#     结束日期 =forms.DateField(disabled=False,required=True,initial=arrow.now().shift(days=0).format('YYYY-MM-DD'),widget=forms.DateInput(attrs={'type': 'date'} ))
#     class Meta:
#         model = models.Run
#         fields = ['ident']    

#         # exclude=['ident']
#     def __init__(self, *args, **kwargs):
#         super(Run_select, self).__init__(*args, **kwargs)

#         for name,field in self.fields.items():
#             field.widget.attrs={'class': 'form-control'}
#             if name=='ident':
#                 field.initial='ident'

# class Run_list(forms.ModelForm):    
#     ident =forms.CharField(disabled=True,initial='ident')#,initial=clean_ident()
#     日期 =forms.DateTimeField(disabled=False,initial=arrow.now().format('YYYY-MM-DD HH:mm:ss'),widget=forms.DateTimeInput(format='%Y-%m-%d %H:%M',
#                                                          attrs={'type': 'datetime-local'}))
#     秒 =forms.IntegerField(disabled=False,initial=0,widget=forms.NumberInput())
#     平均心率=forms.IntegerField(disabled=False,initial=160,widget=forms.NumberInput())
#     距离=forms.FloatField(disabled=False,initial='',widget=forms.NumberInput(),label='距离(公里)')
#     class Meta:
#         model = models.Run
#         fields = ['ident','日期','距离','分钟','秒','平均心率']   
#     def clean_秒(self):        
#         s=self.cleaned_data.get('秒')

#         if s>59:            
#             raise ValidationError("0~59秒")        
#         return s 
#         # exclude=['ident']
#     def __init__(self, *args, **kwargs):
#         super(Run_list, self).__init__(*args, **kwargs)

#         for name,field in self.fields.items():
#             field.widget.attrs={'class': 'form-control'}
#             if name=='ident':
#                 field.initial='ident'
#             if name=='日期':
#                 field.initial=arrow.now().format('YYYY-MM-DD HH:mm:ss')

# class Zi(forms.ModelForm):   
#     ident =forms.CharField(disabled=True,initial='ident')
#     日期=forms.DateTimeField( label='日期', widget=forms.DateTimeInput(format='%Y-%m-%d %H:%M',attrs={'type': 'datetime-local'}))
#     # 横 =forms.CharField(disabled=False,initial=models.Zi.objects.values('横').first()['横'])
#     # 竖 =forms.CharField(disabled=False,initial=models.Zi.objects.values('竖').first()['竖'])
#     class Meta:
#         model = models.Zi
#         fields = '__all__' 

    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for name,field in self.fields.items():
#             field.widget.attrs={'class': 'form-control'}
#             if name=='日期':
#                 field.initial=arrow.now().format('YYYY-MM-DD HH:mm:ss')
#                 field.required=True


# class photo(forms.ModelForm):   
#     ident =forms.CharField(disabled=True,initial='ident')
#     日期=forms.DateTimeField( label='日期', widget=forms.DateTimeInput(format='%Y-%m-%d %H:%M',attrs={'type': 'datetime-local'}))
#     # 横 =forms.CharField(disabled=False,initial=models.Zi.objects.values('横').first()['横'])
#     # 竖 =forms.CharField(disabled=False,initial=models.Zi.objects.values('竖').first()['竖'])
#     class Meta:
#         model = models.photo
#         fields = '__all__' 

    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for name,field in self.fields.items():
#             field.widget.attrs={'class': 'form-control'}
#             if name=='日期':
#                 field.initial=arrow.now().format('YYYY-MM-DD HH:mm:ss')
#                 field.required=True


# # class Shoes_select(forms.ModelForm):    
# #     ident =forms.CharField(disabled=True,initial='ident')#,initial=clean_ident()
# #     开始日期 =forms.DateTimeField(disabled=False,required=True,widget=forms.DateInput(attrs={'type': 'date'} ))
# #     结束日期 =forms.DateField(disabled=False,required=True,initial=arrow.now().shift(days=0).format('YYYY-MM-DD'),widget=forms.DateInput(attrs={'type': 'date'} ))
# #     class Meta:
# #         model = models.Shoes
# #         fields = ['ident']    

# #         # exclude=['ident']
# #     def __init__(self, *args, **kwargs):
# #         super().__init__(*args, **kwargs)

# #         for name,field in self.fields.items():
# #             field.widget.attrs={'class': 'form-control'}
# #             if name=='ident':
# #                 field.initial='ident'
# # class Shoes_list(forms.ModelForm):    

# #     class Meta:
# #         model = models.Shoes
# #         fields = "__all__"    

# #         # exclude=['ident']
# #     def __init__(self, *args, **kwargs):



# #         super().__init__(*args, **kwargs)

# #         for name,field in self.fields.items():
            
# #             field.widget.attrs={'class': 'form-control'}
# #             if name=='ident':
# #                 field.initial='ident'

# class Ti(forms.ModelForm):
#     class Meta:
#         model = Ti_da
#         fields = []# 以列表的形式写入字段




#     ti=[v['题号'] for i,v in enumerate(models.Ti_da.objects.values('题号'))]
#     id=locals()
#     choice=[(v,v) for i,v in enumerate(list('ABCD对错'))]

#     for i in ti:
        
#         id[str(i)] =forms.MultipleChoiceField(choices=choice,required=True,label=str(i))# widget=forms.CheckboxSelectMultiple,
     


#     日期 =forms.DateField(required=True,initial=arrow.now().shift(days=0).format('YYYY-MM-DD'),
#                         error_messages={'required': '由于计划不能为空'}
#                         ,widget=forms.DateInput(format='%Y-%m-%d',attrs={'type': 'date'}),label="日期")
#     def __init__(self, *args, **kwargs) :
#         super().__init__(*args,**kwargs)
#         for name,field in self.fields.items():
#             field.widget.attrs={'class': 'form-control'}

#     # choice=[(v,v) for i,v in enumerate(list('ABCD对错'))]

#     # my_field = forms.MultipleChoiceField(choices=choice, widget=forms.CheckboxSelectMultiple,label='间隔时间(分钟)')

 
# class Bpzd(forms.Form):

#     k=forms.FloatField(required=True,widget=forms.NumberInput(attrs={'class':'form-control'}),label='K',
#         error_messages={'required': '不能为空'})#,initial=clean_ident()IntegerField方法代码示例 - 纯净天空
#     a =forms.FloatField(widget=forms.NumberInput(attrs={'class':'form-control'}), required=True,label='α',
#         error_messages={'required': '不能为空'})#α
#     q =forms.FloatField()
#     v =forms.FloatField()
#     r =forms.FloatField()    
    

    
#     def __init__(self, *args, **kwargs):
#         super(Bpzd, self).__init__(*args, **kwargs)
#         for name,field in self.fields.items():
#             field.widget.attrs={'class': 'form-control'}
#             if name=='k':
#                 field.required=True




# class UserModelForm(forms.ModelForm):
#     class Meta:
#         model = DCustomer1
#         fields = "__all__"# 以列表的形式写入字段
#     # 数量ha =forms.DateField(required=False,widget=forms.NumberInput)
#         # widgets={"姓名":forms.DateInput(attrs={'type':"date"}),
#         #          "电话":forms.PasswordInput()}
#         # 生日t =forms.DateField(required=False,initial=arrow.now().shift(days=0).format('YYYY-MM-DD'),widget=forms.DateInput,label=u"日期")
#         # 数量ha =forms.DateField(required=False,widget=forms.NumberInput)
#     def __init__(self, *args, **kwargs) :
#         super().__init__(*args,**kwargs)
#         for name,field in self.fields.items():
#             field.widget.attrs={'class': 'form-control'}


#     def clean_电话(self):
#         txt_phone=self.cleaned_data['电话']
#         if len(txt_phone)!=11:
#             raise ValidationError("格式错误")
#         return txt_phone
    
#     choice=[(i+1,v) for i,v in enumerate(["男","女"])]
#     性别=forms.ChoiceField(choices=choice,label='性别')
#     生日 =forms.DateField(required=True,
#                             initial=today,
#                             error_messages={'required': '由于计划不能为空'}
#                             ,widget=forms.DateInput(format='%Y-%m-%d',
#                                                          attrs={'type': 'date'})
#                                                          ,label="生日")
#     邮箱=forms.EmailField(required=True,error_messages={'required': '不能为空'},widget=forms.EmailInput,label='邮箱')


#     # choice=[(i+1,v['姓名']) for i,v in enumerate(DCustomer1.objects.values('姓名'))]
#     # 部门=forms.ChoiceField(choices=choice,label='部门')
#     # date=forms.DateField(widget=forms.DateInput(attrs={'type':"date"}),label=u"日期")

#     # email=forms.EmailField(required=False,widget=forms.EmailInput,label='邮箱')
 

# class Weight(forms.ModelForm):
#     class Meta:

#         model = weight1
#         fields = "__all__"# 以列表的形式写入字段
       
#     日期 =forms.DateField(required=True,widget=forms.DateInput(attrs={'type':"date"}),label="日期")
#     体重 =forms.FloatField(required=True,widget=forms.NumberInput(),label="tizhong")



#     def __init__(self, *args, **kwargs) :
#         super().__init__(*args,**kwargs)
#         for name,field in self.fields.items():
#             field.widget.attrs={'class': 'form-control'}

#     def clean_ident(self):
#         txt_ident=self.cleaned_data['ident']
#         if len(txt_ident)!=6:
#             raise ValidationError("格式错误6位数字")
#         return txt_ident
    
# class Tizheng(forms.ModelForm):
#     ident=forms.CharField(disabled=True,initial='ident')

#     class Meta:
#         model = tizheng
#         fields = "__all__"# 以列表的形式写入字段
       
#     日期 =forms.DateField(required=True,initial=arrow.now().shift(days=0).format('YYYY-MM-DD'),widget=forms.DateInput(format='%Y-%m-%d', attrs={'type':'date'}) ,label="日期")
#     #ident =forms.CharField(required=True,label="ident")

#     def __init__(self, *args, **kwargs) :
#         super().__init__(*args,**kwargs)
#         for name,field in self.fields.items():
#             field.widget.attrs={'class': 'form-control'}



