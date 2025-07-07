import re
import ansible_runner
from mycelery.main import app

ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*[mGKH]')
@app.task
def run_ansible_playbook(directory, playbook):
    try:
        runner = ansible_runner.run(
            private_data_dir=directory,
            playbook=playbook,
            quiet=True,
            rotate_artifacts=1
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