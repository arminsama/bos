from django.db import models
from product.models import Product
from employee.models import Employee
# Create your models here.


class Issue(models.Model):
    """
        status = {
            1：等待审批人审批
            2：代码上线中
            3: 代码回滚中
            11:上线完成
            12：上线失败
            13:回滚完成
            14：回滚失败
            15:提案驳回
        }
    """
    title = models.CharField(max_length=128, verbose_name='提案标题')
    comment = models.TextField(max_length=256, verbose_name='提案更改内容说明')
    product_name = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='产品名称')
    creator = models.CharField(max_length=64,  verbose_name='创建人')
    assigner = models.CharField(max_length=64, verbose_name='上线审核人')
    newest_version = models.IntegerField(default=0, verbose_name='将要上线的最新版本')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='提案创建时间')
    last_mtime = models.DateTimeField(auto_now=True, verbose_name='最后修改时间')
    status = models.IntegerField(default=1, verbose_name='提案状态')
    diff_new = models.TextField(blank=True, null=True, default='', verbose_name='新增的文件和文件夹')
    diff_change = models.TextField(blank=True, null=True, default='', verbose_name='变化的文件和文件夹')
    diff_delete = models.TextField(blank=True, null=True, default='', verbose_name='删除的文件和文件夹')
    timeline = models.TextField(blank=True, null=True, default='', verbose_name='时间线信息')
    success_ip = models.TextField(blank=True, null=True, default='', verbose_name='上线成功IP')
    fail_ip = models.TextField(blank=True, null=True, default='', verbose_name='上线失败IP')
    can_rollback = models.BooleanField(default=False, verbose_name='是否可以回滚')

    class Meta:
        db_table = 'issue'
        ordering = ['pk']

    @property
    def need_sa_agree(self):
        choice = Product.objects.get(name=self.product_name).need_sa_agree
        return choice

    @property
    def get_status(self):
        status = {1: '等待审批人审批', 2: '代码上线中', 3: '代码回滚中', 11: '上线成功', 12: '部分上线成功', 13: '上线失败', 14: '回滚成功', 15: '回滚失败', 16: '提案驳回', 17: '部分回滚成功'}
        return status[self.status]

