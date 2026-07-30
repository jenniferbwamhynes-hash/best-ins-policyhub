"""
Backfill migration: set policy_metadata = {} for all existing rows.
Runs in batches of 10,000 to avoid long-running transactions.

Runtime on staging (2.3M rows): 4m 12s
Refs: POLICY-1
"""
from django.db import migrations

def backfill_metadata(apps, schema_editor):
    PolicyDocument = apps.get_model('policy', 'PolicyDocument')
    batch_size = 10_000
    qs = PolicyDocument.objects.filter(policy_metadata__isnull=True)
    count = qs.count()
    processed = 0
    while processed < count:
        batch_ids = list(qs.values_list('id', flat=True)[processed:processed + batch_size])
        PolicyDocument.objects.filter(id__in=batch_ids).update(policy_metadata={})
        processed += len(batch_ids)

class Migration(migrations.Migration):
    dependencies = [('policy', '0042_add_policy_metadata')]
    operations = [migrations.RunPython(backfill_metadata, migrations.RunPython.noop)]
