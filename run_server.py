import os
import subprocess
from Project import settings_local as settings

python_bin = os.path.join(settings.PYTHON_BIN, 'python.exe')


def run_server(name_server):
    script_file = os.path.join(settings.BASE_DIR, f'server_{name_server}.py')
    process = subprocess.Popen([python_bin, script_file])
    return process


def exec_server():

    list_server = []

    process = run_server('nginx')
    if process:
        list_server.append(process)

    process = run_server('api')
    if process:
        list_server.append(process)

    for s in list_server:
        s.wait()


if __name__ == '__main__':
    exec_server()
