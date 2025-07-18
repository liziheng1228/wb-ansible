import os
import re
import time
from tempfile import TemporaryDirectory
import ansible_runner
from asgiref.sync import async_to_sync
from celery import shared_task, current_task
from channels.layers import get_channel_layer
from ansible_runner.config.runner import RunnerConfig
from mycelery.main import app

ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*[mGKH]')


@shared_task
def run_ansible_playbook(**kwargs):
    playbook_content = kwargs.get('playbook')
    job_type = kwargs.get('job_type')
    inventory_dict = kwargs.get('inventory')
    verbosity = kwargs.get('verbosity', 0)
    forks = kwargs.get('forks', 5)
    module_name = kwargs.get('module_name')
    module_args = kwargs.get('module_args')
    extra_vars = kwargs.get('extra_vars')
    ssh_pass = kwargs.get('ssh_pass')
    become_pass = kwargs.get('become_pass')

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
        # 密码传入，不推荐明文保存，测试使用；可以改为免密登录执行任务
        password_dict = {
            "^SSH password:\\s*?$": ssh_pass,
            "^BECOME password.*:\\s*?$": become_pass
        }
        ansible_cfg = """
        [defaults]
        ask_pass      = True
        forks          = 5
        host_key_checking = False
        log_path = ansible.log
        remote_tmp=/tmp

        [privilege_escalation]
        become=true
        become_ask_pass=true
        become_method = sudo
        become_user = root

        [diff]
        scp_if_ssh=True
        """
        with TemporaryDirectory() as temp_dir:
            ansible_cfg_path = os.path.join(temp_dir, 'ansible.cfg')
            playbook_path = os.path.join(temp_dir, 'playbook.yml')

            # 写入配置文件内容到临时文件
            with open(ansible_cfg_path, 'w', encoding='utf-8') as f:
                f.write(ansible_cfg)
            if job_type == "playbook":  # 执行 playbook
                playbook_content = playbook_content

                # 写入Playbook内容到临时文件
                with open(playbook_path, 'w', encoding='utf-8') as f:
                    f.write(playbook_content)

                runner = ansible_runner.run(
                    private_data_dir=temp_dir,
                    inventory=inventory_dict,
                    playbook=playbook_path,
                    quiet=True,
                    verbosity=verbosity,
                    forks=forks,
                    passwords=password_dict,
                    event_handler=event_handler,
                    # rotate_artifacts=1,

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

                runner = ansible_runner.run(
                    private_data_dir=temp_dir,
                    host_pattern='test',  # 主机组
                    inventory=inventory_dict,
                    module=module_name,
                    module_args=module_args,
                    quiet=True,
                    verbosity=verbosity,
                    forks=forks,
                    passwords=password_dict,
                    event_handler=event_handler,
                    # rotate_artifacts=1,

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
