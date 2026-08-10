from django.db import migrations, models


class Migration(migrations.Migration):
    """
    POLICY-7: Add policy_renewal_optin column to policy_documents.

    Zero-downtime approach:
    - Column is nullable with a db_default of True (applied by Postgres at INSERT)
    - Existing rows will have NULL until the backfill migration (0046) runs
    - Application code in RenewalSchedulerService must handle None until backfill completes
    """

    dependencies = [
        ("policyhub", "0044_backfill_null_metadata_hotfix"),
    ]

    operations = [
        migrations.AddField(
            model_name="policydocument",
            name="policy_renewal_optin",
            field=models.BooleanField(
                null=True,
                db_default=True,
                help_text="Whether the policyholder has opted into renewal notifications. "
                          "Null for rows inserted before migration 0045.",
            ),
        ),
    ]
