import json
import re

from ansible_run.tasks import run_ansible_playbook
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync
ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*[mGKH]')



class TaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = f"task_{self.scope['url_route']['kwargs']['task_id']}"

        print(self.group_name)
        # self.group_name = "task_task"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )


    async def task_update(self, event):
        print("Task update received",event['text'])

        await self.send(text_data=json.dumps({
            'status': ANSI_ESCAPE.sub("",event['text']['status']),
            'stdout': ANSI_ESCAPE.sub("",event['text']['stdout']),
            'stderr': ANSI_ESCAPE.sub("",event['text']['stderr'])
        }))


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        task_id = self.scope['url_route']['kwargs']['group']
        async_to_sync(self.channel_layer.group_add)("task_list", self.channel_name)
        print(self.channel_name)
        self.accept()

    def receive(self, text_data):
        print('z',text_data)
        directory = './ansible_runner'
        ply = "test.yaml"
        task_id = run_ansible_playbook.delay(directory, ply)

        # text_data_json = json.loads(text_data)
        async_to_sync(self.channel_layer.group_send)(
            "task_list", {
                "type": "xxx.ooo",
                "text_data": text_data
            }
        )


    def xxx_ooo(self, event):
        message = event['text_data']
        # print((event))

        self.send(text_data=message)  # 同步发送


