from celery import task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@task(name='send_async_mail')
def send_async_mail(message):
    logger.info('Sending email: Subject {}'.format(message.subject))
    return message.send()