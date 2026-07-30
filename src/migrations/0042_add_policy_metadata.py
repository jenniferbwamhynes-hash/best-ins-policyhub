"""
Migration: add policy_metadata JSONB column to policy_documents.

Zero-downtime approach:
  1. Add column with DEFAULT NULL (no table lock beyond ALTER TABLE)
  2. Backfill existing rows in batches of 10,000
  3. Separate follow-up migration will add NOT NULL + GIN index

Refs: POLICY-1, CHG0010001
"""
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('policy', '0041_policy_renewal_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='policydocument',
            name='policy_metadata',
            field=models.JSONField(null=True, blank=True),
        ),
    ]
