#!/usr/bin/env python
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
from cStringIO import StringIO
import sys

Options = namedtuple('Options', ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check'])
variable_manager = VariableManager()
loader = DataLoader()
inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list='/etc/ansible/hosts')
variable_manager.set_inventory(inventory)
options = Options(connection='local', module_path='/root', forks=100, become=None, become_method=None, become_user=None, check=False)
passwords = dict(vault_pass='secret')

class callback_class(CallbackBase):
    def v2_runner_on_ok(self, result, **kwargs):
        try: 
            print 'Host: %' % (result._host)
            for line in result._result['stdout'].split('\n'):
                print line
        except:
            pass

def line_print(input):
    if input and len(input) > 0:
        for line in input.split('\n', ''):
            print line
    else: 
        print 'Nothing to print :('

def run_command(cmd, host):
    callback_ob = callback_class()
    play_source =  dict(
        name = "Ansible Play",
        hosts = host,
        gather_facts = 'no',
        tasks = [
	    dict(action=dict(module='shell', args=cmd), register='shell_out'),
            dict(action=dict(module='debug', args=dict(msg='{{shell_out.stdout}}')))
         ]
    )
    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

    task = TaskQueueManager(
              inventory=inventory,
              variable_manager=variable_manager,
              loader=loader,
              options=options,
              passwords=passwords,
              stdout_callback=callback_ob,
          )
    # redirecting stdout to grab the output from the task
    normal_stdout = sys.stdout
    sys.stdout = new_stdout = StringIO()
    result = task.run(play)
    sys.stdout = normal_stdout
#    import pdb; pdb.set_trace()
    return new_stdout.readlines()


results = run_command('df -h', 'localhost')
line_print(results)
