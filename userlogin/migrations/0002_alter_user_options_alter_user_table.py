# Generated by Django 5.0.3 on 2025-07-01 05:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userlogin', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={},
        ),
        migrations.AlterModelTable(
            name='user',
            table='UserInfo',
        ),
    ]
