from celery import shared_task
import time

@shared_task(bind=True)
def test_task(self):
    a = 500+500
    time.sleep(15)