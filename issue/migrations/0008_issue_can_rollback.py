# Generated by Django 2.0.13 on 2019-03-08 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issue', '0007_auto_20190308_1025'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='can_rollback',
            field=models.BooleanField(default=False, verbose_name='是否可以回滚'),
        ),
    ]