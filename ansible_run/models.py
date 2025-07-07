from django.db import models

# Create your models here.
class CeleryTask(models.Model):


    task_id = models.CharField(max_length=255, primary_key=True)  # 任务唯一标识
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间
    is_used = models.BooleanField(default=False, verbose_name="是否已使用")  # 新增字段
    class Meta:
        verbose_name = "Celery任务记录"
        verbose_name_plural = "Celery任务记录"

    def __str__(self):
        return self.task_id