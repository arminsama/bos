# Generated by Django 2.1.7 on 2019-02-26 10:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('department', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='产品线')),
                ('administrator', models.CharField(max_length=64, verbose_name='产品线管理员')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='department.Department', verbose_name='产品线所属部门')),
            ],
            options={
                'db_table': 'productLine',
                'ordering': ['name'],
            },
        ),
    ]