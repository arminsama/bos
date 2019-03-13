from django.db import models
from django.contrib.auth.models import AbstractUser
from productline.models import ProductLine
# Create your models here.


class Employee(AbstractUser):
    ROLE_CHOICE = (
        ('root', '管理员'),
        ('user', '普通用户')
    )

    username = models.CharField(max_length=50, unique=True, verbose_name='用户名')
    fullname = models.CharField(max_length=100, verbose_name='全名')
    role = models.CharField(choices=ROLE_CHOICE, max_length=10, default='user', verbose_name='身份')
    email = models.EmailField(max_length=100, verbose_name='邮箱')
    phone = models.IntegerField(verbose_name='手机号')
    password = models.CharField(max_length=128, verbose_name='密码')
    productline = models.ForeignKey(ProductLine, on_delete=models.CASCADE, verbose_name='用户所属的产品线')
    is_sa = models.BooleanField(default=False, verbose_name='是否是sa')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='用户创建时间')

    @property
    def is_root(self):
        if self.role == 'root':
            return True
        else:
            return False

    @property
    def display_fullname(self):
        return self.fullname

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'employee'
        ordering = ['pk']
