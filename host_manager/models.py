from django.db import models

class Host(models.Model):
    hostname = models.CharField(max_length=100, verbose_name="主机名")
    ip = models.GenericIPAddressField(verbose_name="IP地址")
    port = models.IntegerField(verbose_name="端口", default=22)  # 默认SSH端口
    username = models.CharField(max_length=50, verbose_name="用户名")
    # 可以增加更多字段，如密码，但注意安全，建议加密存储
    # 密码字段，实际生产环境应该使用加密，这里为了简单使用CharField，但注意：不能明文存储密码
    # password = models.CharField(max_length=200, blank=True, null=True)
    class Meta:
        db_table = "host"
        verbose_name = "主机信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.hostname
