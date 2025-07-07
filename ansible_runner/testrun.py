from ansible_runner import run

directory = '/root/project/ansible_runner'
ply = "test.yaml"


runner = run(private_data_dir=directory,playbook='/root/project/ansible_runner/project/test.yaml',verbosity=0)
