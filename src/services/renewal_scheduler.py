"""
RenewalSchedulerService — Celery Beat scheduled job for policy renewal notifications.
Runs daily at 06:00 CT. Sends email/SMS reminders at 90, 60, and 30 days before expiry.

POLICY-5 | Hotfix for INC — ORM null guard added for policy_renewal_optin
"""

from datetime import date, timedelta
import logging

from celery import shared_task

from policyhub.models import PolicyDocument
from policyhub.services.notification_template_service import NotificationTemplateService

logger = logging.getLogger(__name__)

REMINDER_DAYS = [90, 60, 30]


@shared_task(name="renewal_scheduler.send_renewal_reminders", bind=True, max_retries=3)
def send_renewal_reminders(self):
    """
    Find all policies with upcoming renewals and dispatch reminder notifications.
    Treats policy_renewal_optin=None as True (db_default intent for pre-migration rows).
    """
    today = date.today()
    sent = 0
    errors = 0

    for days_out in REMINDER_DAYS:
        cutoff = today + timedelta(days=days_out)

        # Use __in=[True, None] so pre-migration rows (where ORM returns None despite
        # db_default=True) are treated as opted-in. Migration 0046 backfills these to
        # True permanently; this guard is a safety net for the transition window.
        candidates = PolicyDocument.objects.filter(
            policy_renewal_optin__in=[True, None],
            expiry_date=cutoff,
            status="active",
        ).select_related("insured")

        for policy in candidates:
            try:
                NotificationTemplateService.send_renewal_reminder(
                    policy=policy,
                    days_until_expiry=days_out,
                )
                sent += 1
            except Exception as exc:
                logger.error(
                    "Failed to send renewal reminder for policy %s: %s",
                    policy.policy_number,
                    exc,
                )
                errors += 1

    logger.info("Renewal reminder job complete: sent=%d errors=%d", sent, errors)
    return {"sent": sent, "errors": errors}
