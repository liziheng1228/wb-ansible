from ansible_runner import run

directory = '/opt/wb-ansible/ansible_runner'
ply = "test.yaml"

envvars={
        'ANSIBLE_PYTHON_INTERPRETER': '/usr/bin/python'
}
runner = run(private_data_dir=directory,playbook='/root/project/ansible_runner/project/test.yaml')
