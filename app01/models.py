from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

# Create your models here.
class User(models.Model):
    """用户表"""
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=64)

class Admin(models.Model):
    # id = models.BigAutoField(primary_key=True)
    ident = models.CharField(max_length=32)
    username = models.CharField(max_length=32)
    role = models.CharField(max_length=32, verbose_name='身份')  # 修改字段名称
    password = models.CharField(max_length=64)
    department = models.CharField(max_length=32, default='')

    avatar = models.ImageField(upload_to='avatars/admin/',  # 存储路径
                            null=True,
                            blank=True,
                            default='avatars/admin/default_avatar.png')  # 默认路径

class QuestionType(models.Model):
    id = models.AutoField(primary_key=True)
    question_type = models.CharField(max_length=20)
    tihao = models.CharField(max_length=20)
    question = models.TextField()  # 修改为TextField
    options = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=20)

class JskjgQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    question_type = models.CharField(max_length=20)
    tihao = models.CharField(max_length=20)
    question = models.TextField()  # 修改为TextField
    options = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=20)

class WxpzxQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    question_type = models.CharField(max_length=20)
    tihao = models.CharField(max_length=20)
    question = models.TextField()  # 修改为TextField
    options = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=20)

class UserAnswer(models.Model):

    ti_type = models.CharField(max_length=20)
    tihao = models.CharField(max_length=20)
    date = models.DateField()    
    ident = models.CharField(max_length=20)

    # def __str__(self):
    #     return self.UserAnswer

class Tihao(models.Model):
    题号=models.TextField(blank=False, null=False) 

class LoginRecords(models.Model):

    ip = models.CharField(verbose_name='ip',max_length=32)
    time = models.DateTimeField(blank=False, null=False,auto_now_add=True)
    ident= models.CharField(max_length=32, default='')
    name = models.CharField(verbose_name='用户名',max_length=32)
    job = models.CharField(verbose_name='职位',max_length=32)
    type = models.CharField(verbose_name='登入登出',max_length=32)

    # class Meta:
    #     verbose_name = '登录记录'
    #     verbose_name_plural = verbose_name
    #     ordering = ['-time']
    # def __str__(self):
    #     return self.name

class ExplosiveInventoryItem(models.Model):
    """
    库存物品模型

    该模型用于存储民爆仓库管理系统中的库存物品信息。
    """
    # 出入库状态，选项为'出库'或'入库'，默认值为'出库'
    inventory_status = models.CharField(max_length=10, choices=[('出库', '出库'), ('入库', '入库')], default='出库', verbose_name='出入库状态')
    # 项目部
    project_department = models.CharField(max_length=100, verbose_name='项目部')
    # 出入库单号

    blaster = models.CharField(max_length=100, verbose_name='爆破员', default='')

    detonating_device_quantity = models.IntegerField(default=0, verbose_name='起爆具(个)')
    # 导爆索长度(米)，默认值为0
    detonating_cord_length = models.IntegerField(default=0, verbose_name='导爆索(米)')

        # 新增字段
    # 32乳化数量(公斤)，默认值为0
    emulsion_explosive_32mm = models.IntegerField(default=0, verbose_name='32乳化(公斤)')
    # 2号粉箱数量(箱)，默认值为0
    powdery_explosive_box_2 = models.IntegerField(default=0, verbose_name='2号粉箱(公斤)')
    # 粘药数量(公斤)，默认值为0
    sticky_explosive = models.IntegerField(default=0, verbose_name='粘药(公斤)')
    # 5米电子雷管数量(发)，默认值为0
    electronic_detonator_5m = models.IntegerField(default=0, verbose_name='5米电子雷管(发)')
    # 15米电子雷管数量(发)，默认值为0
    electronic_detonator_15m = models.IntegerField(default=0, verbose_name='15米电子雷管(发)')

    # 日期
    date = models.DateField(verbose_name='日期')

class CategoryContent(models.Model):
    """
    种类内容模型

    该模型用于存储种类和内容信息。
    """
    category = models.CharField(max_length=100, verbose_name='种类')
    content = models.CharField(max_length=100, verbose_name='内容')

    def __str__(self):
        return f"{self.category} - {self.content}"

class UploadedPDF(models.Model):
    # 定义一个字段来存储上传的PDF文件
    model_name = models.CharField(max_length=100, default='')
    pdf_file = models.FileField(upload_to='pdfs/')

class UploadedTu(models.Model):
    # 定义一个字段来存储上传的PDF文件
    model_name = models.CharField(max_length=100, default='')
    pdf_file = models.FileField(upload_to='tu/')    

class UploadedZhaopian(models.Model):
    # 定义一个字段来存储上传的PDF文件
    name = models.CharField(max_length=10, blank=True, null=True, verbose_name='姓名')  # 新增姓名字段
    photo = models.FileField(upload_to='photo/', verbose_name='原始照片')  # 添加verbose_name

    rotated_photo = models.ImageField(
        upload_to='rotated/', 
        default='', 
        verbose_name='排版'  # 已存在保持不动
    )

    blue_background = models.ImageField(
        upload_to='blue_background/',
        verbose_name='蓝底',  # 修改此处
        blank=True,
        null=True,
        default=''
    )
    red_background = models.ImageField(
        upload_to='red_background/',
        verbose_name='红底',  # 修改此处
        blank=True,
        null=True,
        default=''
    )
    white_background = models.ImageField(
        upload_to='white_background/',
        verbose_name='白底',  # 修改此处
        blank=True,
        null=True,
        default=''
    )

    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')  # 添加verbose_name

class IDCard(models.Model):
    name = models.CharField(max_length=100, verbose_name='姓名')
    id_number = models.CharField(max_length=18, verbose_name='身份证号')
    front_image = models.ImageField(
        upload_to='ids/', 
        verbose_name='人像面照片'
    )
    back_image = models.ImageField(
        upload_to='ids/',
        verbose_name='国徽面照片'
    )
    combined_image = models.ImageField(
        upload_to='combined/',
        verbose_name='双面合成图',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

class ContractLabor(models.Model):
    name = models.CharField(max_length=4, verbose_name='姓名')
    id_number = models.CharField(max_length=18, verbose_name='身份证号')

    contract_file = models.FileField(
        upload_to='contractlabor/', 
        verbose_name='劳动合同'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

class Candidate(models.Model):
    GENDER_CHOICES = [('男', '男性'), ('女', '女性')]
    MARITAL_CHOICES = [('未婚', '未婚'), ('已婚', '已婚')]
    LICENSE_CHOICES = [('有', '有驾照'), ('无', '无驾照')]

    name = models.CharField(max_length=20, verbose_name='姓名')
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, verbose_name='性别')

    mobile = models.CharField(
        max_length=11, 
        verbose_name='手机', 
        default='',  # 修复: 从default=30改为空字符串
        blank=False
    )

    age= models.IntegerField(
        verbose_name='年龄',
        null=True,
        blank=True, 
        default=30,
        validators=[MinValueValidator(18), MaxValueValidator(65)]  # 添加数值范围验证
    )

    marital_status = models.CharField(max_length=2, choices=MARITAL_CHOICES, verbose_name='婚姻状况')
    education = models.CharField(max_length=50, verbose_name='学历+专业')
    has_driver_license = models.CharField(max_length=2, choices=LICENSE_CHOICES, verbose_name='驾照')
    special_skills = models.TextField(verbose_name='特长')
    work_experience = models.TextField(verbose_name='工作经历')
    current_address = models.CharField(verbose_name='现住所', max_length=10, blank=True, default='')
    position = models.CharField(max_length=20, verbose_name='应聘岗位', default='')
    expected_salary = models.CharField(max_length=20, verbose_name='期望薪资')
    photo = models.ImageField(
        upload_to='candidate_photos/',
        verbose_name='一寸照',  # 修改此处的verbose_name
        blank=True,
        null=True
    )
    # 新增简历文件字段
    resume_file = models.FileField(
        upload_to='resumes/',
        verbose_name='简历文件',
        blank=True,default='',
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '求职者档案'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_gender_display()}"

class ExplosiveStaff(models.Model):
    name = models.CharField(max_length=100, verbose_name='姓名')
    id_number = models.CharField(max_length=18, verbose_name='身份证号')    
    mobile = models.CharField(
    max_length=11, 
    verbose_name='电话号',
        blank=True,default='',
        null=True
    )

    # 新增银行卡号字段
    bank_card_number = models.CharField(
        max_length=19,
        verbose_name='银行卡号',
        blank=True,
        null=True,
        default='',
        validators=[
            RegexValidator(  # 移除 models. 前缀
                regex=r'^\d{16}$|^\d{19}$',
                message='银行卡号必须为16或19位数字'
            )
        ]
    )

    front_image = models.ImageField(upload_to='explosive_staff/', verbose_name='人像面照片')  
    back_image = models.ImageField(upload_to='explosive_staff/', verbose_name='国徽面照片')  
    combined_image = models.ImageField(upload_to='explosive_staff/', verbose_name='双面合成图')

    photo = models.FileField(upload_to='explosive_staff/photo/', verbose_name='1寸照片')  
    typeset_photo = models.ImageField(upload_to='explosive_staff/', verbose_name='排版后照片')

    no_crime = models.ImageField(
        upload_to='explosive_staff/',
        verbose_name='无犯罪证明',
        blank=True,  # 新增：允许表单为空
        null=True    # 新增：允许数据库存储NULL
    )  
    graduation = models.ImageField(
        upload_to='explosive_staff/', 
        verbose_name='毕业证',
        blank=True,  # 新增：允许表单为空
        null=True    # 新增：允许数据库存储NULL
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

class WeighingRecord(models.Model):
    weight_number = models.CharField(
        max_length=12,
        verbose_name='磅单号',
        validators=[
            RegexValidator(
                regex=r'^(岩石\d{10}|\d{12})$',  # 修改正则表达式
                message='必须为岩石+10位纯数字 或 12位纯数字'
            )
        ]
    )
    truck_driver = models.CharField(max_length=50, verbose_name='大车司机')  # 字段名改为英文
    forklift_driver = models.CharField(max_length=50, verbose_name='铲车司机')  # 字段名改为英文
    net_weight = models.IntegerField(verbose_name='矿石净重（kg）')  # 字段名改为英文
    weight_photo = models.ImageField(  # 字段名改为英文
        upload_to='weighing_records/',
        verbose_name='称重单照片'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return f"{self.weight_number} - {self.created_at.strftime('%Y-%m-%d')}"  # 同步修改字段引用

    def clean(self):
        if self.weight_number == '岩石' and self.net_weight <= 0:  # 同步修改字段引用
            raise ValidationError('岩石类型必须填写重量')

# ... 其他模型保持不变 ...

class BlastingCertificate(models.Model):
    """爆破作业人员证书模型"""
    certificate_number = models.CharField(
        max_length=13,  # 修改长度为13
        verbose_name='证书编号',
        unique=True,
        validators=[  # 添加数字验证
            RegexValidator(
                regex=r'^\d{13}$',
                message='证书编号必须为13位数字'
            )
        ]
    )
    name = models.CharField(
        max_length=4,  # 姓名长度改为4
        verbose_name='姓名'
    )
    certificate_photo = models.ImageField(  # 新增照片字段
        upload_to='blasting_certificates/',
        verbose_name='爆破证照片',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        verbose_name = '爆破员证书'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.certificate_number} - {self.name}"

# ... 原有模型保持不变 ...

#cd OneDrive\lnjx && python manage.py makemigrations

#python manage.py makemigrations
#python manage.py migrate

class Blaster(models.Model):
    """爆破员"""
    name = models.CharField(max_length=50, verbose_name='爆破员')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')

    class Meta:
        verbose_name = '爆破员'
        verbose_name_plural = '爆破员'

    def __str__(self):
        return self.name

class BlastingSummary(models.Model):
    """雷管炸药台账汇总"""
    shift = models.CharField(max_length=20, blank=True, verbose_name="班次")
    person = models.CharField(max_length=50, verbose_name='人员')
    location = models.CharField(max_length=100, verbose_name='地点')
    date = models.CharField(max_length=20, verbose_name='日期')
    detonator_count = models.IntegerField(default=0, verbose_name='雷管数')
    explosive_count = models.IntegerField(default=0, verbose_name='炸药数(公斤)')
    blaster = models.CharField(max_length=50, blank=True, verbose_name="爆破员")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    segments_data = models.JSONField(default=dict, blank=True, verbose_name="分段数据")

    class Meta:
        verbose_name = '雷管炸药台账'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.person} - {self.date} - 雷管{self.detonator_count}发"

class BlastingSitePhoto(models.Model):
    """爆破现场记录照片"""
    code = models.CharField(max_length=50, verbose_name='编号', blank=True, null=True)
    location = models.CharField(max_length=100, verbose_name='爆破地点')
    photo = models.FileField(upload_to='blasting_site/', verbose_name='现场照片')
    blaster = models.CharField(max_length=50, verbose_name='爆破员', blank=True, default='')
    safety_officer = models.CharField(max_length=50, verbose_name='安全员', blank=True, default='')
    engineer = models.CharField(max_length=50, verbose_name='工程师', blank=True, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')

    class Meta:
        verbose_name = '爆破现场记录'
        verbose_name_plural = '爆破现场记录'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.location} - {self.uploaded_at.strftime("%Y-%m-%d %H:%M")}'

class PushSubscription(models.Model):
    """Web push subscription for PWA notifications"""
    endpoint = models.CharField(max_length=255, unique=True, verbose_name='推送端点')
    p256dh = models.TextField(blank=True, default='', verbose_name='p256dh密钥')
    auth = models.TextField(blank=True, default='', verbose_name='auth密钥')
    user_agent = models.TextField(blank=True, default='', verbose_name='用户代理')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '推送订阅'
        verbose_name_plural = '推送订阅'
        ordering = ['-created_at']

    def __str__(self):
        return f'Push sub {self.id} ({self.created_at.strftime("%Y-%m-%d")})'
