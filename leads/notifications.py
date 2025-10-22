# leads/notifications.py
from django.conf import settings
from django.core.mail import send_mail
import logging

log = logging.getLogger(__name__)

def email_notify(subject: str, message: str, html_message: str | None = None):
    recipients = getattr(settings, "NOTIFY_EMAILS", [])
    if not recipients:
        log.warning("NOTIFY_EMAILS is empty; skipping email notification.")
        return
    send_mail(
        subject=subject,
        message=message,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=recipients,
        html_message=html_message,
        fail_silently=True,   # prod’da xatoni logga yozishni afzal ko‘ramiz
    )

def telegram_notify(text: str):
    """Ixtiyoriy: sozlangan bo‘lsa Telegramga yuboradi."""
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    chat_id = getattr(settings, "TELEGRAM_ADMIN_CHAT_ID", "")
    if not token or not chat_id:
        return
    try:
        import requests
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": text})
    except Exception as e:
        log.exception("Telegram notify failed: %s", e)
