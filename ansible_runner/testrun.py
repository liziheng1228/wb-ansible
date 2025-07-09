from ansible_runner import run

directory = '/opt/wb-ansible/ansible_runner'
ply = "test.yaml"

inventory={

  "test1": {
    "hosts": {
      "192.168.1.10": {},
      "192.168.1.11": {}
    }
  },
  "test2": {
    "hosts": {
      "192.168.1.12": {},
      "192.168.1.13": {}
    }
  }

}


runner = run(private_data_dir=directory,playbook=ply,inventory=inventory)
