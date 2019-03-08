from django.db import models

# Create your models here.


class Department(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='部门')
    comment = models.TextField(blank=True, verbose_name='部门信息')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'department'
        ordering = ['name']
