from django.urls import re_path
from django.urls import path
from tasksocket import consumers

websocket_urlpatterns = [

    re_path(r'ws/task/(?P<task_id>[0-9a-f-]{36})/?$', consumers.TaskConsumer.as_asgi()),
]
