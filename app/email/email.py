from threading import Thread
from flask_mail import Message
from app import mail


def send_email(subject, recipient, sender, html_body):
    msg = Message(subject=subject, recipients=recipient, sender=sender)
    msg.html = html_body
    mail.send(msg)
    