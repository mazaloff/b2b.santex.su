import time
import os
import subprocess
from Project import settings_local as settings


def exec_server():
    python_bin = os.path.join(settings.PYTHON_BIN, 'python.exe')

    script_file = os.path.join(settings.BASE_DIR, 'server_nginx.py')
    subprocess.Popen([python_bin, script_file])
    script_file = os.path.join(settings.BASE_DIR, 'server_api.py')
    subprocess.Popen([python_bin, script_file])


if __name__ == '__main__':
    exec_server()
    while True:
        time.sleep(60)
