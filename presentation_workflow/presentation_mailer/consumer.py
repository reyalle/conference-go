import json
import pika
import django
import os
import sys
from django.core.mail import send_mail


sys.path.append("")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "presentation_mailer.settings")
django.setup()

parameters = pika.ConnectionParameters(host='rabbitmq')
connection = pika.BlockingConnection(parameters)
channel = connection.channel()


def process_approval(ch, method, properties, body):
    content = json.loads(body)
    name = content["presenter_name"]
    title = content["title"]
    send_mail(
        "Your presentation has been accepted",
        f"{name}, we're happy to tell you that your presentaion {title} has been accepted",
        "admin@conference.go",
        [content["presenter_email"]],
        fail_silently=False,
    )

channel.queue_declare(queue='presentation_approvals')
channel.basic_consume(
    queue='presentation_approvals',
    on_message_callback=process_approval,
    auto_ack=True,
)


def process_rejection(ch, method, properties, body):
    content = json.loads(body)
    name = content["presenter_name"]
    title = content["title"]
    send_mail(
        "Your presentation has been rejected",
        f"{name}, we're sad to tell you that your presentaion {title} has been rejected",
        "admin@conference.go",
        [content["presenter_email"]],
        fail_silently=False,
    )

channel.queue_declare(queue='presentation_rejections')
channel.basic_consume(
    queue='presentation_rejections',
    on_message_callback=process_rejection,
    auto_ack=True,
)
channel.start_consuming()
