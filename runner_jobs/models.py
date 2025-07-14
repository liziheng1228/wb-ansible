from django.db import models
import uuid
from django.utils import timezone
from edit_code.models import PlaybookCode


class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('playbook', 'Playbook'),
        ('adhoc', 'Ad-Hoc 命令'),
    ]
    inventory = models.ManyToManyField('host_manager.Host', verbose_name='目标主机')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('任务名称', max_length=255)
    job_type = models.CharField('任务类型', max_length=10, choices=JOB_TYPE_CHOICES)


    # 如果是 adhoc 类型，存储模块和命令
    module_name = models.CharField('模块名（如 shell/command）', max_length=64, blank=True, null=True)
    module_args = models.CharField('模块参数', max_length=512, blank=True, null=True)

    # 可选字段
    extra_vars = models.TextField('额外变量（JSON格式）', blank=True, null=True)  # 如 {"user": "admin"}
    forks = models.PositiveIntegerField('并发数', default=5)
    verbosity = models.PositiveIntegerField('日志详细程度（0~5）', default=0)
    # Playbook 相关
    playbook = models.ForeignKey(
        PlaybookCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='关联的 Playbook'
    )
    # 如果是 playbook 类型，存储内容或路径
    playbook_content = models.TextField('Playbook 内容（YAML）', blank=True, null=True)
    # 可选：如果是从文件加载的 playbook，可以加个路径字段
    playbook_path = models.CharField('Playbook 文件路径', max_length=512, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.name} ({self.job_type})"

    class Meta:
        verbose_name = "Ansible 任务"
        verbose_name_plural = "Ansible 任务列表"