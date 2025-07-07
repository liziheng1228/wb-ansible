# 变量是固定的 写别的无法访问到
BROKER_URL = 'redis://192.168.56.140:6379/1'
CELERY_RESULT_BACKEND = 'redis://192.168.56.140:6379/2'
CELERY_TIMEZONE = 'Asia/Shanghai'