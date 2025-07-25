# Generated by Django 5.2.4 on 2025-07-24 14:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ansible_run', '0002_celerytask_job'),
        ('runner_jobs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='celerytask',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='celery_tasks', to='runner_jobs.job', verbose_name='所属任务'),
        ),
    ]
