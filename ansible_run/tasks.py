import re
import ansible_runner
from asgiref.sync import async_to_sync
from celery import shared_task, current_task
from channels.layers import get_channel_layer
from ansible_runner.config.runner import RunnerConfig
from mycelery.main import app

ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*[mGKH]')

runner_uid = []


@shared_task
def run_ansible_playbook(directory,playbook=None, job_type=None, inventory=None, verbosity=0, forks=5,
                         playbook_content=None, module_name=None, module_args=None, extra_vars=None):
    print(inventory)

    # 通过 Channels 推送至对应 WebSocket 组
    # 定义 Ansible 事件回调

    def event_handler(event):
        channel_layer = get_channel_layer()

        # print('event_data', event.get('stdout', ''))
        data = {
            'status': event.get('event', 'unknown'),
            'stdout': event.get('stdout', ''),
            'stderr': event.get('stderr', ''),
            'task_id': current_task.request.id
        }
        async_to_sync(channel_layer.group_send)(data['task_id'], {
            "type": "task.update",
            "text": data,
        })

    try:

        print(job_type)
        if job_type == "playbook":# 执行 playbook
            print('playbook')
            runner = ansible_runner.run(
                private_data_dir=directory,
                inventory=inventory,
                playbook=playbook,
                quiet=True,
                rotate_artifacts=0,
                event_handler=event_handler,
                verbosity=verbosity,
                forks=forks,
                json_mode=True


            )
            stdout = runner.stdout.read()
            stderr = runner.stderr.read()
            clean_stdout = ANSI_ESCAPE.sub('', stdout)
            clean_stderr = ANSI_ESCAPE.sub('', stderr)

            return {
                'stdout': clean_stdout,
                'stderr': clean_stderr,
                'rc': runner.rc
            }
        elif job_type == "ad-hoc":
            print('adhoc')

            runner = ansible_runner.run(
                inventory=inventory,
                json_mode=True,
                module=module_name,
                module_args=module_args,
                host_pattern='test', # 主机组
                quiet=True,
                private_data_dir=directory,
                verbosity=verbosity,
                forks=forks,
                event_handler=event_handler,
                rotate_artifacts=0
            )
        # # 执行 playbook 命令

        # 等待任务完成并捕获输出（需根据需求调整）
            stdout = runner.stdout.read()
            stderr = runner.stderr.read()
            clean_stdout = ANSI_ESCAPE.sub('', stdout)
            clean_stderr = ANSI_ESCAPE.sub('', stderr)

            return {
                'stdout': clean_stdout,
                'stderr': clean_stderr,
                'rc': runner.rc
            }
    except Exception as e:
        return {'status': -1, 'error': str(e)}

# print('runner_uid',runner_uid)
