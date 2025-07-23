import json
import re

from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer

ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*[mGKH]')


class TaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        # 获取组名称 与 task中的task_task123 保持一致才能调用到task_update函数
        async_to_sync(channel_layer.group_send)("task_task123", {
            "type": "task.update",
            "text": data,
        })

        """
        self.group_name = f"{self.scope['url_route']['kwargs']['task_id']}"
        print(self.group_name)
        # self.group_name = "task_task123"

        # 将组名称和通道名称一起加入一个组内；self.channel_name是固定写法不可修改
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    # 断开连接操作
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # 回调函数，将内容返回给前端
    async def task_update(self, event):
        await self.send(text_data=json.dumps({
            'status': ANSI_ESCAPE.sub("",event['text']['status']),
            'stdout': ANSI_ESCAPE.sub("",event['text']['stdout']),
            'stderr': ANSI_ESCAPE.sub("",event['text']['stderr'])
        }))
    async def task_stop(self, event):
        await self.send(text_data=json.dumps({

            'stdout': ANSI_ESCAPE.sub("",event['text']['stdout']),

        }))