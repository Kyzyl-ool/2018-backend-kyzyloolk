from app import celery
from .emails import send_mail

sender = 'kyzyloolk@mail.ru'
subject = 'TEST'
recipient = 'kyzyl.okm@phystech.edu'
message = 'Hello world'

@celery.task()
def send_report():
    # filename = generate_report()
    send_mail(subject, sender, [recipient], 'Hello world', '<body>Hello</body>')

@celery.task()
def run_main_task(text):
    print(text)

