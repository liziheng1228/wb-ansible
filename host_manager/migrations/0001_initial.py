# Generated by Django 5.2.3 on 2025-07-08 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hostname', models.CharField(max_length=100, verbose_name='主机名')),
                ('ip', models.GenericIPAddressField(verbose_name='IP地址')),
                ('port', models.IntegerField(default=22, verbose_name='端口')),
                ('username', models.CharField(max_length=50, verbose_name='用户名')),
            ],
            options={
                'verbose_name': '主机信息',
                'verbose_name_plural': '主机信息',
                'db_table': 'host',
            },
        ),
    ]
