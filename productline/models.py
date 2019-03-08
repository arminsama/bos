from django.db import models
from department.models import Department
# Create your models here.


class ProductLine(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name='产品线')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='产品线所属部门')
    administrator = models.CharField(max_length=64, verbose_name='产品线管理员')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'productLine'
        ordering = ['name']
