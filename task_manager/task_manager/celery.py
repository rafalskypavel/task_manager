from __future__ import absolute_import
import eventlet
eventlet.monkey_patch()  # Должно быть ПЕРВОЙ инструкцией

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_manager.settings')

app = Celery('task_manager')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.timezone = 'UTC'
app.conf.enable_utc = True

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')