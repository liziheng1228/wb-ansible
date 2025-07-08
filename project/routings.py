from django.urls import re_path

from tasksocket import consumers

websocket_urlpatterns = [
    # re_path(r'^ws/task/$', consumers.TaskConsumer.as_asgi()),
    # re_path(r'ws/(?P<group>\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/task/(?P<task_id>\w+)/$', consumers.TaskConsumer.as_asgi()),

]
