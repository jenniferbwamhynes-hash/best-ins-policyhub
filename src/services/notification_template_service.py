"""
NotificationTemplateService — renders and dispatches policy renewal notification emails/SMS.

Supports:
  - Email via SendGrid (primary)
  - SMS via Twilio (for policyholders with mobile on file)

POLICY-7
"""

import logging
from typing import Literal

from django.conf import settings
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

ReminderType = Literal["90_day", "60_day", "30_day"]

REMINDER_SUBJECTS = {
    90: "Your Best Insurance policy renews in 90 days",
    60: "Action may be required — your policy renews in 60 days",
    30: "Final reminder — your Best Insurance policy renews in 30 days",
}


class NotificationTemplateService:

    @staticmethod
    def send_renewal_reminder(policy, days_until_expiry: int) -> bool:
        """
        Render and send a renewal reminder notification for the given policy.

        Args:
            policy: PolicyDocument instance
            days_until_expiry: One of 90, 60, or 30

        Returns:
            True if at least one channel (email or SMS) succeeded.
        """
        subject = REMINDER_SUBJECTS.get(days_until_expiry, "Policy renewal reminder")
        context = {
            "policy_number": policy.policy_number,
            "insured_name": policy.insured.display_name,
            "expiry_date": policy.expiry_date.strftime("%B %-d, %Y"),
            "days_until_expiry": days_until_expiry,
            "renewal_quote_url": f"https://portal.bestinsurance.com/renew/{policy.policy_number}",
        }

        success = False

        # Email
        if policy.insured.email:
            try:
                html_body = render_to_string(
                    f"notifications/renewal_{days_until_expiry}day.html", context
                )
                NotificationTemplateService._send_email(
                    to=policy.insured.email,
                    subject=subject,
                    html_body=html_body,
                )
                success = True
                logger.debug("Sent %d-day email for %s", days_until_expiry, policy.policy_number)
            except Exception as exc:
                logger.warning("Email send failed for %s: %s", policy.policy_number, exc)

        # SMS (30-day only)
        if days_until_expiry == 30 and policy.insured.mobile_phone:
            try:
                sms_body = (
                    f"Best Insurance: Your policy {policy.policy_number} renews on "
                    f"{context['expiry_date']}. Renew at {context['renewal_quote_url']}"
                )
                NotificationTemplateService._send_sms(
                    to=policy.insured.mobile_phone,
                    body=sms_body,
                )
                success = True
                logger.debug("Sent 30-day SMS for %s", days_until_expiry, policy.policy_number)
            except Exception as exc:
                logger.warning("SMS send failed for %s: %s", policy.policy_number, exc)

        return success

    @staticmethod
    def _send_email(to: str, subject: str, html_body: str):
        # SendGrid integration — placeholder for actual implementation
        if not settings.SENDGRID_API_KEY:
            logger.info("[DRY RUN] Would send email to %s: %s", to, subject)
            return
        # import sendgrid; sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY); ...
        raise NotImplementedError("SendGrid integration not yet wired")

    @staticmethod
    def _send_sms(to: str, body: str):
        # Twilio integration — placeholder for actual implementation
        if not getattr(settings, "TWILIO_ACCOUNT_SID", None):
            logger.info("[DRY RUN] Would send SMS to %s", to)
            return
        raise NotImplementedError("Twilio integration not yet wired")
