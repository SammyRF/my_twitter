from kombu import Queue
import sys

print(__name__ + ' loaded.')

# celery -A twitter worker -l INFO
# CELERY_BROKER_URL = 'redis://127.0.0.1:6379/2' if not TESTING else 'redis://127.0.0.1:6379/0'
CELERY_BROKER_URL = 'amqp://guest@localhost'
CELERY_TIMEZONE = "UTC"
CELERY_TASK_ALWAYS_EAGER = ((" ".join(sys.argv)).find('manage.py test') != -1)
CELERY_QUEUES = (
    Queue('default', routing_key='default'),
    Queue('newsfeeds', routing_key='newsfeeds'),
)
