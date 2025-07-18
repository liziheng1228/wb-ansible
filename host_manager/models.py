from django.db import models
from userlogin.models import User
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


def derive_key(ip: str, username: str) -> bytes:
    """使用 IP + 用户名生成加密密钥"""
    salt = b'host_password_salt_v3'  # 可考虑放在 settings.py 中
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key_material = (ip + username).encode()
    key = base64.urlsafe_b64encode(kdf.derive(key_material))  # 32字节密钥
    return key


class Host(models.Model):
    hostname = models.CharField(max_length=100, verbose_name="主机名")
    ip = models.GenericIPAddressField(verbose_name="IP地址")
    port = models.IntegerField(verbose_name="端口", default=22)
    username = models.CharField(max_length=50, verbose_name="用户名")

    # 加密存储的密码字段
    ssh_password_encrypted = models.BinaryField('加密后的SSH密码', null=True, blank=True)
    become_password_encrypted = models.BinaryField('加密后的提权密码', null=True, blank=True)

    # 关联用户表
    users = models.ManyToManyField(
        User,
        related_name='hosts',
        verbose_name='可用该主机的用户',
        blank=True
    )

    class Meta:
        db_table = "host"
        verbose_name = "主机信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.hostname

    def set_ssh_password(self, ssh_password: str):
        """加密存储 SSH 密码"""
        key = derive_key(self.ip, self.username)
        fernet = Fernet(key)
        self.ssh_password_encrypted = fernet.encrypt(ssh_password.encode())

    def get_ssh_password(self) -> str:
        """解密获取 SSH 密码"""
        if not self.ssh_password_encrypted:
            return ""
        key = derive_key(self.ip, self.username)
        fernet = Fernet(key)
        return fernet.decrypt(self.ssh_password_encrypted).decode()

    def set_become_password(self, become_password: str):
        """加密存储 Become 密码"""
        key = derive_key(self.ip, self.username)
        fernet = Fernet(key)
        self.become_password_encrypted = fernet.encrypt(become_password.encode())

    def get_become_password(self) -> str:
        """解密获取 Become 密码"""
        if not self.become_password_encrypted:
            return ""
        key = derive_key(self.ip, self.username)
        fernet = Fernet(key)
        return fernet.decrypt(self.become_password_encrypted).decode()