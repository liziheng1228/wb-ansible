from celery import Celery
import time
import os


"""
 celery 启动命令
    位置为mycelery 目录上一层
    /usr/local/python3/bin/celery -A mycelery.main worker --loglevel=info
"""
# 加载celery配置文件

# 必须要将django的环境变量加进去（在manage.py中复制）
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
#  创建Celery实例化对象
app = Celery("app01")
app.config_from_object("mycelery.config")

app.autodiscover_tasks()


