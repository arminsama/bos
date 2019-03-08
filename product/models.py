from django.db import models
from employee.models import Employee

# Create your models here.


class Product(models.Model):
    SYNC_TYPE_CHOICE = (
        ('t', '测试'),
        ('g', '灰度'),
        ('o', '线上'),
        ('tg', '测试+灰度'),
        ('to', '测试+线上'),
        ('go', '灰度+线上'),
        ('tgo', '测试+灰度+线上'),
    )

    SYNC_OPTION_CHOICE = (
        ('incremental', '增量上线'),
        ('full', '全量上线'),
    )
    name = models.CharField(max_length=128, unique=True, verbose_name='产品名称')
    comment = models.TextField(max_length=300, blank=True, null=True, verbose_name='产品描述')
    ################
    employees = models.ManyToManyField(Employee, verbose_name='产品拥有人')
    domain = models.CharField(max_length=256, null=True, blank=True, verbose_name='产品域名')
    git_address = models.URLField(unique=True, verbose_name='Git地址')
    product_dir = models.CharField(max_length=128, unique=True, verbose_name='线上代码目录')
    #   上线方式、地址选项 测试or灰度or线上
    #   sync_mode
    sync_type = models.CharField(choices=SYNC_TYPE_CHOICE, max_length=20, verbose_name='上线类型_测试or灰度or线上')
    test_ip_list = models.TextField(max_length=500, blank=True, null=True, verbose_name='测试机器地址', help_text='逗号分割')
    gray_ip_list = models.TextField(max_length=500, blank=True, null=True, verbose_name='灰度机器地址', help_text='逗号分割')
    online_ip_list = models.TextField(max_length=500, blank=True, null=True, verbose_name='上线机器地址', help_text='逗号分割')
    #   上线的方式选项 全量更新or增量更新   |    不同步文件或目录选项选项
    #   sync_file_option
    sync_option = models.CharField(choices=SYNC_OPTION_CHOICE, max_length=64, verbose_name='上线选项_全量or增量')
    no_sync_file_and_path = models.TextField(max_length=500, blank=True, null=True, verbose_name='不同步的文件或者目录换行分割')

    command_before_sync = models.CharField(max_length=256, blank=True, null=True, verbose_name='上线前需要执行的命令')
    command_after_sync = models.CharField(max_length=256, blank=True, null=True, verbose_name='上线后需要执行的命令')

    need_sa_agree = models.BooleanField(default=True, verbose_name='是否需要sa同意')
    send_email = models.BooleanField(default=False, verbose_name='是否发送通知邮件')
    send_msg = models.BooleanField(default=False, verbose_name='是否发送通知短信')

    version = models.IntegerField(default=1, verbose_name='当前代码版本')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='产品创建时间')
    last_edit_time = models.DateTimeField(auto_now=True, verbose_name='产品最后更新时间')

    def __str__(self):
        return self.name

    def get_sync_type(self):
        sync_type_dict = {
            't': '测试',
            'g': '灰度',
            'o': '线上',
            'tg': '测试+灰度',
            'to': '测试+线上',
            'go': '灰度+线上',
            'tgo': '测试+灰度+线上'}
        return sync_type_dict[self.sync_type]

    def get_sync_option(self):
        sync_option = {'incremental': '增量上线', 'full': '全量上线'}
        return sync_option[self.sync_option]

    def get_need_sa_agree(self):
        if self.need_sa_agree is True:
            return '是'
        else:
            return '否'

    def get_send_email(self):
        if self.send_email is True:
            return '是'
        else:
            return '否'

    def get_send_msg(self):
        if self.send_msg is True:
            return '是'
        else:
            return '否'

    class Meta:
        db_table = 'product'
        ordering = ['create_time']
