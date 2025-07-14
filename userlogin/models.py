from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    # 添加额外的字段

    class Meta:
        db_table = 'UserInfo'
        unique_together = ('email','username')
        verbose_name_plural = '用户'

    def __str__(self):
        return self.username