#!/usr/bin/env python
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase


Options = namedtuple('Options', ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check'])
variable_manager = VariableManager()
loader = DataLoader()
inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list='/etc/ansible/hosts')
variable_manager.set_inventory(inventory)
options = Options(connection='local', module_path='/root', forks=100, become=None, become_method=None, become_user=None, check=False)
passwords = dict(vault_pass='secret')

class df_output_callback(CallbackBase):
    def v2_runner_on_ok(self, result, **kwargs):
        try: 
            print result._host
            for line in result._result['stdout'].split('\n'):
                print line
        except:
            pass

def run_command(cmd, host):
    if cmd == 'df -h':
        results_callback = df_output_callback()
        play_source =  dict(
            name = "Ansible Play",
            hosts = host,
            gather_facts = 'no',
            tasks = [
                dict(action=dict(module='shell', args=cmd), register='shell_out')
             ]
        )
        play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

    tqm = TaskQueueManager(
              inventory=inventory,
              variable_manager=variable_manager,
              loader=loader,
              options=options,
              passwords=passwords,
              stdout_callback=results_callback,
          )
    result = tqm.run(play)


run_command('df -h', 'localhost')
