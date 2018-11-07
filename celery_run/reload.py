import psutil
import os
import subprocess
import sys

list_ = psutil.pids()
kill = ('python.exe', 'flower.exe', 'celery.exe')

for i in list_:
    try:
        p = psutil.Process(i)
    except psutil.NoSuchProcess:
        continue
    if p.name() in kill and os.getpid() != p.pid:
        try:
            p.terminate()
        except psutil.AccessDenied:
            continue

subprocess.Popen('SCHTASKS /End /TN \celery\server', shell=True, stdout=sys.stdout)
subprocess.Popen('SCHTASKS /End /TN \celery\start_worker', shell=True, stdout=sys.stdout)
subprocess.Popen('SCHTASKS /End /TN \celery\start_beat', shell=True, stdout=sys.stdout)
subprocess.Popen('SCHTASKS /End /TN \celery\start_flower', shell=True, stdout=sys.stdout)

subprocess.Popen('SCHTASKS /Run /TN \celery\server', shell=True, stdout=sys.stdout)
subprocess.Popen('SCHTASKS /Run /TN \celery\start_worker', shell=True, stdout=sys.stdout)
subprocess.Popen('SCHTASKS /Run /TN \celery\start_beat', shell=True, stdout=sys.stdout)
subprocess.Popen('SCHTASKS /Run /TN \celery\start_flower', shell=True, stdout=sys.stdout)
