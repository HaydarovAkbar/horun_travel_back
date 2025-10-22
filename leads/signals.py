# leads/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import escape
from django.utils.translation import gettext as _
from django.db.models.signals import pre_save

from .models import Application, ContactMessage
from .notifications import email_notify, telegram_notify


@receiver(post_save, sender=Application)
def on_application_created(sender, instance: Application, created: bool, **kwargs):
    if not created:
        return
    # # Email matn
    # subject = f"🟢 Yangi ariza: {instance.full_name}"
    # lines = [
    #     _("Ism") + f": {instance.full_name}",
    #     _("Telefon") + f": {instance.phone}",
    #     _("Email") + f": {instance.email or '—'}",
    #     _("Tanlangan tur") + f": {getattr(instance.tour, 'title', None) or '—'}",
    #     _("Muqobil yo‘nalish") + f": {instance.alt_destination or '—'}",
    #     _("Boshlanish sanasi") + f": {instance.desired_start_date or '—'}",
    #     _("Kunlar") + f": {instance.days or '—'}",
    #     _("Kattalar/Bolalar/Chaqaloqlar") + f": {instance.adults}/{instance.children}/{instance.infants}",
    #     _("Byudjet") + f": {instance.budget_from or '—'}–{instance.budget_to or '—'} {instance.currency}",
    #     _("Aloqa usuli") + f": {instance.get_preferred_contact_display()}",
    #     _("Izoh") + f": {instance.message or '—'}",
    #     "",
    #     _("Texnik") + ":",
    #     f"IP: {instance.client_ip or '—'}",
    #     f"UA: {instance.user_agent[:120] + '…' if instance.user_agent and len(instance.user_agent) > 120 else instance.user_agent or '—'}",
    #     f"Referrer: {instance.referrer or '—'}",
    # ]
    # message = "\n".join(lines)
    # email_notify(subject, message)

    # Telegram (qisqaroq)
    tg = (
        f"🟢 Yangi ariza\n"
        f"Ism: {instance.full_name}\n"
        f"Tel: {instance.phone}\n"
        f"Tur: {getattr(instance.tour, 'title', None) or '—'}\n"
        f"Boshlanish: {instance.desired_start_date or '—'}\n"
        f"Byudjet: {instance.budget_from or '—'}–{instance.budget_to or '—'} {instance.currency}\n"
        f"Holat: {instance.get_status_display()}"
    )
    telegram_notify(tg)


@receiver(post_save, sender=ContactMessage)
def on_contact_created(sender, instance: ContactMessage, created: bool, **kwargs):
    if not created:
        return
    # subject = f"📩 Yangi kontakt xabar: {instance.full_name}"
    # lines = [
    #     _("Ism") + f": {instance.full_name}",
    #     _("Email") + f": {instance.email or '—'}",
    #     _("Telefon") + f": {instance.phone or '—'}",
    #     _("Mavzu") + f": {instance.get_subject_display()}",
    #     _("Xabar") + f": {instance.message}",
    #     "",
    #     _("Texnik") + ":",
    #     f"IP: {instance.client_ip or '—'}",
    #     f"UA: {instance.user_agent[:120] + '…' if instance.user_agent and len(instance.user_agent) > 120 else instance.user_agent or '—'}",
    #     f"Referrer: {instance.referrer or '—'}",
    # ]
    # message = "\n".join(lines)
    # email_notify(subject, message)

    tg = (
        f"📩 Yangi xabar\n"
        f"Ism: {instance.full_name}\n"
        f"Email: {instance.email or '—'}\n"
        f"Tel: {instance.phone or '—'}\n"
        f"Mavzu: {instance.get_subject_display()}"
    )
    telegram_notify(tg)


@receiver(pre_save, sender=Application)
def on_application_status_changed(sender, instance: Application, **kwargs):
    if not instance.pk:
        return  # yangi yaratilayotganda emas
    try:
        old = Application.objects.get(pk=instance.pk)
    except Application.DoesNotExist:
        return
    if old.status != instance.status:
        # subject = f"🔄 Application status o'zgardi: {old.get_status_display()} → {instance.get_status_display()}"
        msg = f"{instance.full_name} / {getattr(instance.tour, 'title', None) or '—'}"
        # email_notify(subject, msg)
        telegram_notify(f"🔄 Ariza status: {old.get_status_display()} → {instance.get_status_display()}\n{msg}")
