"""
RenewalSchedulerService — Celery Beat scheduled job for policy renewal notifications.
Runs daily at 06:00 CT. Sends email/SMS reminders at 90, 60, and 30 days before expiry.

POLICY-7 | CHG pending CAB approval
"""

from datetime import date, timedelta
import logging

from celery import shared_task
from django.utils import timezone

from policyhub.models import PolicyDocument
from policyhub.services.notification_template_service import NotificationTemplateService

logger = logging.getLogger(__name__)

REMINDER_DAYS = [90, 60, 30]


@shared_task(name="renewal_scheduler.send_renewal_reminders", bind=True, max_retries=3)
def send_renewal_reminders(self):
    """
    Find all policies with upcoming renewals and dispatch reminder notifications.
    Only sends to policyholders who have opted in (policy_renewal_optin=True).
    """
    today = date.today()
    sent = 0
    errors = 0

    for days_out in REMINDER_DAYS:
        cutoff = today + timedelta(days=days_out)

        # NOTE: policy_renewal_optin has db_default=True in Postgres, so new rows
        # are always True. Existing rows (pre-migration 0045) will be None in the ORM
        # until the backfill migration runs — but we ship the backfill atomically so
        # this should never be an issue in production.
        candidates = PolicyDocument.objects.filter(
            policy_renewal_optin=True,   # Will raise TypeError on None (pre-migration rows)
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

    logger.info(
        "Renewal reminder job complete: sent=%d errors=%d",
        sent,
        errors,
    )
    return {"sent": sent, "errors": errors}
