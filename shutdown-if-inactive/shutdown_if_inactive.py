import os.path
import requests
import json
from azureml.core import Workspace
from azureml.core.compute import ComputeInstance
from datetime import datetime

IDLE_THRESHOLD_IN_SEC = 3600

# Jupyter runs on Compute Instance on http on port 8888
NOTEBOOK_SESSION_URL = f'http://localhost:8888/api/sessions'
NOTEBOOK_TERMINAL_URL = f'http://localhost:8888/api/terminals'

def get_compute_instance_name():
    instance = None
    ci_path = "/mnt/azmnt/.nbvm"
    if os.path.isfile(ci_path):
        with open(ci_path, 'r') as f:
            instance = dict(x.strip().split('=') for x in f)
    return instance['instance']

def was_recently_updated(ts):
    timestamp = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fz")
    return (datetime.now() - timestamp).total_seconds() < IDLE_THRESHOLD_IN_SEC

def get_notebook_sessions():
    notebooks = requests.get(NOTEBOOK_SESSION_URL).json()
    return [{
        "path": nb['path'],
        "state": nb['kernel']['execution_state'],
        "num_connections": nb['kernel']['connections'],
        "last_activity": nb['kernel']['last_activity'],
        "recently_updated": was_recently_updated(nb['kernel']['last_activity']),
    } for nb in notebooks]

def get_notebook_terminals():
    terminals = requests.get(NOTEBOOK_TERMINAL_URL).json()
    return [{
        "name": tr["name"],
        "last_activity": tr['last_activity'],
        "recently_updated": was_recently_updated(tr['last_activity']),
    } for tr in terminals]

def are_all_notebooks_idle(notebooks):
    for n in notebooks:
        if (n['state'] != 'idle' or n["recently_updated"]):
            return False
    return True

def are_all_terminals_idle(terminals):
    for t in terminals:
        if (t["recently_updated"]):
            return False
    return True

def get_instance_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
    return uptime_seconds

def is_compute_idle(uptime):
    return uptime > IDLE_THRESHOLD_IN_SEC

notebooks = get_notebook_sessions()
terminals = get_notebook_terminals()
ci_name = get_compute_instance_name()
instance_uptime = get_instance_uptime()

# print debug data to console
print(f"Checking if Compute Instance {ci_name} is idle")
print(f"> MAX Idle Time: {IDLE_THRESHOLD_IN_SEC} s")
print(f"> VM Uptime:     {instance_uptime} s")
print()
print("> Notebooks")
print(json.dumps(notebooks, indent=2))
print("> Terminals")
print(json.dumps(terminals, indent=2))
print("")

if are_all_notebooks_idle(notebooks) and are_all_terminals_idle(terminals) and instance_uptime > IDLE_THRESHOLD_IN_SEC:
    print('RESULT: Compute Instance is idle and will be shut down.')
    # Connect to workspace and stop instance
    ws = Workspace.from_config()
    ct = ComputeInstance(ws, ci_name)
    ct.stop(wait_for_completion=False, show_output=False)
else:
    print('RESULT: Compute Instance has notebooks and terminals running or just started, will NOT be shut down.')
