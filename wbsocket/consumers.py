from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync

class ChatConsumer(WebsocketConsumer):
    def websocket_connect(self, event):
        self.accept()

    def websocket_receive(self, event):
        print(event)
        self.send("回复恢复")

    def websocket_disconnect(self, event):
        raise StopConsumer()