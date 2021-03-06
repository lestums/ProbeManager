import logging
from smtplib import SMTPException

import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from lxml import html as html_lxml
from pushbullet import Pushbullet

from home.models import Configuration

logger = logging.getLogger('home')


def send_notification(title, body, html=False):
    if html:
        plain_body = html_lxml.fromstring(body).text_content()
        html_body = body
    else:
        plain_body = body
        html_body = '<pre>' + body + '</pre>'
    # Pushbullet
    if Configuration.get_value("PUSHBULLET_API_KEY"):
        pb = Pushbullet(Configuration.get_value("PUSHBULLET_API_KEY"))
        push = pb.push_note(title, plain_body)
        logger.debug(push)
    # Splunk
    if Configuration.get_value("SPLUNK_HOST"):
        if Configuration.get_value("SPLUNK_USER") and Configuration.get_value("SPLUNK_PASSWORD"):
            url = "https://" + Configuration.get_value(
                "SPLUNK_HOST") + ":8089/services/receivers/simple?source=ProbeManager&sourcetype=notification"
            r = requests.post(url, verify=False, data=html_body,
                              auth=(Configuration.get_value("SPLUNK_USER"), Configuration.get_value("SPLUNK_PASSWORD")))
        else:
            url = "https://" + Configuration.get_value(
                "SPLUNK_HOST") + ":8089/services/receivers/simple?source=ProbeManager&sourcetype=notification"
            r = requests.post(url, verify=False, data=html_body)
        logger.debug("Splunk " + str(r.text))
    # Email
    users = User.objects.all()
    if settings.DEFAULT_FROM_EMAIL:
        try:
            for user in users:
                if user.is_superuser:
                    user.email_user(title, plain_body, html_message=html_body, from_email=None)
        except SMTPException as e:
            logger.error(str(e))


@receiver(post_save, sender=User)
def my_handler(sender, instance, **kwargs):
    send_notification(sender.__name__ + " created", str(instance.username) + " - " + str(instance.email))
