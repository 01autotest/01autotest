@echo off
del /q /s "D:\autotest_platform\celerybeat.pid"
python manage.py celery beat
pause