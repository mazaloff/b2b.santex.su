import os
import sys
from time import sleep

import psutil
import subprocess
import requests

import Project.settings_local as settings

python_bin = sys.executable
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
                            print('Terminate server', name_server)
                            sleep(5)
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
    print('Start server', name_server)
    return process


def server_alive(name_server: str, point: tuple):
    try:
        answer = requests.get(f'http://{point[0]}:{point[1]}')
    except requests.exceptions.ConnectionError:
        print('Server died', name_server)
        return False

    if answer.status_code != 200:
        print('Server died', name_server)
        return False

    print('Server alive', name_server)
    return True


def check_servers():
    servers = {'nginx': settings.SERVER_NGINX, 'api': settings.SERVER_ARI}

    while True:
        for name, point in servers.items():
            if server_alive(name, point):
                sleep(60)
            else:
                run_server(name)
                sleep(5)


def exec_server():

    run_server('nginx')
    run_server('api')

    sleep(10)

    check_servers()


if __name__ == '__main__':

    dir_base = os.path.dirname(os.path.abspath(__file__))
    os.chdir(dir_base)
    if dir_base not in sys.path:
        sys.path.append(dir_base)

    path_dir = settings.BASE_DIR

    exec_server()
