import re
import ansible_runner
from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer

from mycelery.main import app

ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*[mGKH]')


@app.task
def run_ansible_playbook(directory, playbook):
    channel_layer = get_channel_layer()

    # 通过 Channels 推送至对应 WebSocket 组
    # 定义 Ansible 事件回调
    def event_handler(event):
        # print('event_data', event.get('stdout', ''))
        data = {
            'status': event.get('event', 'unknown'),
            'stdout': event.get('stdout', ''),
            'stderr': event.get('stderr', ''),
            # 'task_id': self.request.id
        }
        async_to_sync(channel_layer.group_send)("task_task123", {
            "type": "task.update",
            "text": data,
        })

    try:
        runner = ansible_runner.run(
            private_data_dir=directory,
            playbook=playbook,
            quiet=True,
            rotate_artifacts=1,
            event_handler=event_handler,
        )
        # 等待任务完成并捕获输出（需根据需求调整）
        stdout = runner.stdout.read()
        stderr = runner.stderr.read()
        clean_stdout = ANSI_ESCAPE.sub('', stdout)
        clean_stderr = ANSI_ESCAPE.sub('', stderr)
        # print("输出：",output)
        return {
            'stdout': clean_stdout,
            'stderr': clean_stderr,
            'rc': runner.rc
        }
    except Exception as e:
        return {'status': -1, 'error': str(e)}
