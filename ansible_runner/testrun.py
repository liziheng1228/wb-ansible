from ansible_runner import run

directory = '/opt/wb-ansible/ansible_runner'
ply = "test.yaml"
inventory_dict = {
    "test": {
        "hosts": {
            '192.168.56.140': {
                "ansible_host": '192.168.56.140',
                "ansible_port": 22,
                "ansible_user": 'lzh',
            }
        }
    }
}
forks=5
module_name = 'shell'
module_args='ls /root'
verbosity=3
r = run(
    inventory=inventory_dict,
    module=module_name,
    module_args=module_args,
    host_pattern='test', # 主机组
    private_data_dir=directory,
    verbosity=verbosity,
    forks=forks,
)
#print("{}: {}".format(r.status, r.rc))
#print(r.stdout.read())

#runner = run(private_data_dir=directory,playbook=ply,inventory=inventory)
