import os
import time
import subprocess
import psutil


python_bin = ''
path_dir = ''


def get_pid(name_file):
    with open(name_file, 'r+') as file:
        list_str = file.readlines()
        pid = list_str[0] if len(list_str) > 0 else None
        return pid


def terminate_server_name_exe(name, sleep_after=5):
    list_pid = psutil.pids()
    for i in list_pid:
        try:
            p = psutil.Process(i)
        except psutil.NoSuchProcess:
            continue
        if p.name() == name:
            try:
                p.terminate()
                time.sleep(sleep_after)
            except psutil.AccessDenied:
                pass


def terminate_server_pid(pid, sleep_after=5):
    list_pid = psutil.pids()
    for i in list_pid:
        try:
            p = psutil.Process(i)
        except psutil.NoSuchProcess:
            continue
        if pid == str(p.pid) and p.name():
            try:
                p.terminate()
                time.sleep(sleep_after)
            except psutil.AccessDenied:
                pass


def terminate_server():

    pid_file = os.path.join(path_dir, 'celerybeat.pid')
    if os.path.exists(pid_file):
        pid = get_pid(pid_file)
        if pid:
            terminate_server_pid(pid)
        os.remove(os.path.abspath(pid_file))

    terminate_server_name_exe('celery.exe')
    terminate_server_name_exe('flower.exe')

    list_servers = ('worker', 'beat', 'flower')

    for name_server in list_servers:
        pid_file = os.path.join(path_dir, f'server_{name_server}.pid')
        if os.path.exists(pid_file):
            pid = get_pid(pid_file)
            if pid:
                terminate_server_pid(pid)
            os.remove(os.path.abspath(pid_file))


def run_worker():
    name_server = 'worker'
    file_pid = os.path.join(path_dir, f'server_{name_server}.pid')
    process = subprocess.Popen('celery.exe -A san_site worker -l info -P eventlet', shell=True)
    with open(file_pid, 'w') as file:
        file.write(str(process.pid))
    return process


def run_beat():
    name_server = 'beat'
    file_pid = os.path.join(path_dir, f'server_{name_server}.pid')
    process = subprocess.Popen('celery.exe -A san_site beat -l info --pidfile=".\pid\celerybeat.pid"', shell=True)
    with open(file_pid, 'w') as file:
        file.write(str(process.pid))
    return process


def run_flower():
    name_server = 'flower'
    file_pid = os.path.join(path_dir, f'server_{name_server}.pid')
    process = subprocess.Popen('flower.exe --port=5555"', shell=True)
    with open(file_pid, 'w') as file:
        file.write(str(process.pid))
    return process


def exec_server():

    terminate_server()

    list_server = []

    process = run_worker()
    if process:
        list_server.append(process)

    process = run_beat()
    if process:
        list_server.append(process)

    process = run_flower()
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
    path_dir = os.path.join(settings.BASE_DIR, 'pid')

    exec_server()
