# Generated by Django 2.1.7 on 2019-02-28 02:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_auto_20190227_1628'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='employee',
            new_name='employees',
        ),
    ]