import os
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
def run_ansible_playbook(directory, playbook=None, job_type=None, inventory=None, verbosity=0, forks=5,
                         playbook_content=None, module_name=None, module_args=None, extra_vars=None):
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
        # 密码传入，不推荐明文保存，测试使用；可以改为免密登录执行任务
        password_dict = {
            "^SSH password:\\s*?$": "1",
            "^BECOME password.*:\\s*?$": "1"
        }
        if job_type == "playbook":  # 执行 playbook
            ansible_cfg = """[defaults]
            inventory      = inventory
            #callback_whitelist = profile_tasks
            #bin_ansible_callbacks = True 
            ask_pass      = True
            forks          = 10
            host_key_checking = False
            log_path = ansible.log
            remote_tmp=/tmp

            [inventory]
            [privilege_escalation]
            become=true
            become_method = sudo
            become_user = root
            become_ask_pass=true
            [paramiko_connection]
            [ssh_connection]
            [persistent_connection]
            [accelerate]
            [selinux]
            [colors]
            [diff]
            scp_if_ssh=True
            """
            playbook_content = playbook

            from tempfile import TemporaryDirectory
            with TemporaryDirectory() as temp_dir:
                print(temp_dir)
                ansible_cfg_path = os.path.join(temp_dir, 'ansible.cfg')
                playbook_path = os.path.join(temp_dir, 'playbook.yml')

                # ✅ 写入内容到临时文件
                with open(ansible_cfg_path, 'w', encoding='utf-8') as f:
                    f.write(ansible_cfg)

                # ✅ 写入内容到临时文件
                with open(playbook_path, 'w', encoding='utf-8') as f:
                    f.write(playbook_content)

                runner = ansible_runner.run(
                    private_data_dir=temp_dir,
                    inventory=inventory,
                    playbook=playbook_path,
                    quiet=True,
                    rotate_artifacts=1,
                    event_handler=event_handler,
                    verbosity=verbosity,
                    forks=forks,
                    passwords=password_dict

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
                module=module_name,
                module_args=module_args,
                host_pattern='test',  # 主机组
                quiet=True,
                private_data_dir=directory,
                verbosity=verbosity,
                forks=forks,
                event_handler=event_handler,
                rotate_artifacts=1
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
