# Generated by Django 2.1.7 on 2019-02-26 10:19

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='产品名称')),
                ('comment', models.TextField(blank=True, max_length=300, null=True, verbose_name='产品描述')),
                ('domain', models.CharField(max_length=256, verbose_name='产品域名')),
                ('git_path', models.URLField(unique=True, verbose_name='Git地址')),
                ('project_dir', models.CharField(max_length=128, unique=True, verbose_name='上线代码存放目录')),
                ('sync_type', models.CharField(choices=[('t', '测试'), ('g', '灰度'), ('o', '线上'), ('tg', '测试+灰度'), ('to', '测试+线上'), ('go', '灰度+线上'), ('tgo', '测试+灰度+线上')], max_length=20, verbose_name='上线地址选项_测试or灰度or线上')),
                ('test_ip_list', models.TextField(blank=True, help_text='换行分割', max_length=500, null=True, verbose_name='测试机器地址')),
                ('gray_ip_list', models.TextField(blank=True, help_text='换行分割', max_length=500, null=True, verbose_name='灰度机器地址')),
                ('online_ip_list', models.TextField(blank=True, help_text='换行分割', max_length=500, null=True, verbose_name='上线机器地址')),
                ('sync_option', models.CharField(choices=[('incremental', '增量上线'), ('full', '全量上线')], max_length=64, verbose_name='上线方式_全量or增量')),
                ('no_sync_file_and_path', models.TextField(blank=True, help_text='换行分割', max_length=500, null=True, verbose_name='不同步的文件或者目录')),
                ('command_before_sync', models.CharField(blank=True, max_length=256, null=True, verbose_name='上线前需要执行的命令')),
                ('command_after_sync', models.CharField(blank=True, max_length=256, null=True, verbose_name='上线后需要执行的命令')),
                ('need_sa_agree', models.BooleanField(default=True, verbose_name='是否需要sa同意')),
                ('send_email', models.BooleanField(default=False, verbose_name='是否发送通知邮件')),
                ('send_msg', models.BooleanField(default=False, verbose_name='是否发送通知短信')),
                ('version', models.IntegerField(default=1, verbose_name='当前代码版本')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='产品创建时间')),
                ('last_edit_time', models.DateTimeField(auto_now=True, verbose_name='产品最后更新时间')),
                ('employee', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='产品拥有人')),
            ],
            options={
                'db_table': 'product',
                'ordering': ['create_time'],
            },
        ),
    ]