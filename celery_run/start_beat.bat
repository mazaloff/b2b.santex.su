@echo off
call C:\Users\mazal\Python\Project\Environment\Scripts\activate.bat
if /i exist %cd%\celerybeat.pid (
    DEL %cd%\celerybeat.pid
    )
call CD ..
celery -A san_site beat -l info --pidfile=".\celery_run\celerybeat.pid"