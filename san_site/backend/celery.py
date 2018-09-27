import celery
import celery.bin.base
import celery.bin.celery
import celery.platforms
from django.conf import settings

from Project.celery import app

from kombu import Connection
from kombu.exceptions import KombuError


def celery_is_up():
    if settings.CELERY_NO_GET_STATUS:
        return True
    if not is_connection():
        return False
    try:
        status = celery.bin.celery.CeleryCommand.commands['status']()
        status.app = app
        status.run()
        return True
    except celery.bin.base.Error as e:
        if e.status == celery.platforms.EX_UNAVAILABLE:
            return False
        raise e


def is_connection():
    celery_broker_url = "amqp://localhost"
    try:
        conn = Connection(celery_broker_url)
        conn.ensure_connection(max_retries=1)
        return True
    except KombuError:
        return False
