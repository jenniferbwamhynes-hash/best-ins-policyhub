"""
Hotfix migration: set policy_metadata = {} for any remaining null rows.
Rows inserted between migration 0042 and 0043 backfill completion
may still have null values.

Refs: INC0010001, POLICY-8
"""
from django.db import migrations

def backfill_null_metadata(apps, schema_editor):
    PolicyDocument = apps.get_model('policy', 'PolicyDocument')
    updated = PolicyDocument.objects.filter(
        policy_metadata__isnull=True
    ).update(policy_metadata={})
    print(f'Backfilled {updated} rows with null policy_metadata')

class Migration(migrations.Migration):
    dependencies = [('policy', '0043_backfill_policy_metadata')]
    operations = [migrations.RunPython(backfill_null_metadata, migrations.RunPython.noop)]
