import os
import time
from sys import stderr

import psutil
import subprocess

python_bin = ''
path_dir = ''


def terminate_server(name_server):
    pid_file = os.path.join(path_dir, 'pid', f'server_{name_server}.pid')
    if os.path.exists(pid_file):
        with open(pid_file, 'r+') as file:
            list_str = file.readlines()
            pid = list_str[0] if len(list_str) > 0 else None
            if pid:
                list_pid = psutil.pids()
                for i in list_pid:
                    try:
                        p = psutil.Process(i)
                    except psutil.NoSuchProcess:
                        continue
                    if p.name() == 'python.exe' and pid == str(p.pid):
                        try:
                            p.terminate()
                            time.sleep(5)
                        except psutil.AccessDenied:
                            pass
        os.remove(os.path.abspath(pid_file))


def run_server(name_server):
    terminate_server(name_server)
    file_pid = os.path.join(path_dir, 'pid', f'server_{name_server}.pid')
    script_file = os.path.join(path_dir, 'Project', f'server_{name_server}.py')

    access_file_path = os.path.join(path_dir, 'logs', f'{name_server}_access.log')
    error_file_path = os.path.join(path_dir, 'logs', f'{name_server}_error.log')

    if not os.path.exists(os.path.join(path_dir, 'logs')):
        os.mkdir(os.path.join(path_dir, 'logs'))

    access_file = open(access_file_path, mode='a+', encoding='utf-8-sig')
    error_file = open(error_file_path, mode='a+', encoding='utf-8-sig')

    process = subprocess.Popen([python_bin, script_file], stdout=access_file, stderr=error_file)
    with open(file_pid, 'w') as file:
        file.write(str(process.pid))
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

    import sys

    dir_base = os.path.dirname(os.path.abspath(__file__))
    os.chdir(dir_base)
    if dir_base not in sys.path:
        sys.path.append(dir_base)

    import Project.settings_local as settings

    python_bin = os.path.join(settings.PYTHON_BIN, 'python.exe')
    path_dir = settings.BASE_DIR

    exec_server()
