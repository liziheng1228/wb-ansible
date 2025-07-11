from ansible_runner import run

directory = '/opt/wb-ansible/ansible_runner'
ply = "test.yaml"

inventory={

  "test": {
    "hosts": {
      "192.168.1.10": {},
      "192.168.1.11": {}
    }
  },
  "test": {
    "hosts": {
      "192.168.56.142": {},
      "192.168.1.13": {}
    }
  }

}
forks=5
module_name = 'shell'
module_args='ls'
verbosity=0
r = run(
    inventory=inventory,
    module=module_name,
    module_args=module_args,
    host_pattern='test', # 主机组
    quiet=False,
    private_data_dir=directory,
    verbosity=verbosity,
    forks=forks,
)
#print("{}: {}".format(r.status, r.rc))
#print(r.stdout.read())

#runner = run(private_data_dir=directory,playbook=ply,inventory=inventory)
