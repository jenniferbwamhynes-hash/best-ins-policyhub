from django.db import migrations


class Migration(migrations.Migration):
    """
    Hotfix backfill: set policy_renewal_optin=True for all rows where it is NULL.

    Migration 0045 added the column with db_default=True, which Postgres applies at
    INSERT time. Rows that existed before 0045 have NULL in the ORM until this backfill
    runs. The scheduler's __in=[True, None] guard covers the window between 0045 and
    this migration; once this runs all rows are explicitly True or False.
    """

    dependencies = [
        ("policyhub", "0045_add_policy_renewal_optin"),
    ]

    operations = [
        migrations.RunSQL(
            sql="UPDATE policy_documents SET policy_renewal_optin = TRUE WHERE policy_renewal_optin IS NULL;",
            reverse_sql="-- no reverse: cannot distinguish original NULLs from backfilled rows",
        ),
    ]
