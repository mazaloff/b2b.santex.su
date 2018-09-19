@echo off
call C:\Users\mazal\Python\Project\Environment\Scripts\activate.bat
call CD ..
celery -A san_site worker -l info -P eventlet