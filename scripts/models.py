# playbook/models.py

from django.db import models
from django.utils import timezone
from userlogin.models import User


class Script(models.Model):
    SCRIPT_TYPE_CHOICES = [
        ('shell', 'Shell 脚本'),
        ('playbook', 'Playbook 脚本'),
    ]
    name = models.CharField("名称", max_length=255)
    description = models.TextField("描述", blank=True, null=True)
    content = models.TextField("脚本内容")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # 创建者绑定user模型
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="创建者",
        related_name="scripts"
    )

    script_type = models.CharField(
        "脚本类型",
        max_length=20,
        choices=SCRIPT_TYPE_CHOICES,
        default='playbook'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "脚本"
        verbose_name_plural = "脚本"
        unique_together = ('created_by', 'name')
