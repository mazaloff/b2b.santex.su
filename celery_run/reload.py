import psutil
import os
import subprocess
import sys

list_ = psutil.pids()
kill = ('python.exe', 'flower.exe', 'celery.exe')

for i in list_:
    p = psutil.Process(i)
    if p.name() in kill and os.getpid() != p.pid:
        p.terminate()

subprocess.Popen('SCHTASKS /End /TN \celery\start_worker', shell=True, stdout=sys.stdout)
subprocess.Popen('SCHTASKS /End /TN \celery\start_beat', shell=True, stdout=sys.stdout)
subprocess.Popen('SCHTASKS /End /TN \celery\start_flower', shell=True, stdout=sys.stdout)

subprocess.Popen('SCHTASKS /Run /TN \celery\start_worker', shell=True, stdout=sys.stdout)
subprocess.Popen('SCHTASKS /Run /TN \celery\start_beat', shell=True, stdout=sys.stdout)
subprocess.Popen('SCHTASKS /Run /TN \celery\start_flower', shell=True, stdout=sys.stdout)
