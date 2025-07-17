# playbook/models.py

from django.db import models
from django.utils import timezone
from userlogin.models import User

class PlaybookCode(models.Model):
    name = models.CharField("名称", max_length=255)
    description = models.TextField("描述", blank=True, null=True)
    content = models.TextField("YAML 内容")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    # 创建者绑定user模型
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="创建者",
        related_name="playbooks"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Playbook"
        verbose_name_plural = "Playbooks"
        unique_together = ('created_by', 'name')