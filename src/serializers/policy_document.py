from rest_framework import serializers
from ..models.policy_document import PolicyDocument

class PolicyDocumentSerializer(serializers.ModelSerializer):
    """
    HOTFIX applied 2026-07-21 — INC0010001 / POLICY-8

    policy_metadata may be NULL for rows that existed before the CHG0010001
    migration backfill completed. Both SerializerMethodFields must guard
    against None before calling .get() — dict methods are not available on None.
    """
    metadata_version = serializers.SerializerMethodField()
    compliance_flags = serializers.SerializerMethodField()

    def get_metadata_version(self, obj):
        metadata = obj.policy_metadata or {}  # guard against null
        return metadata.get('version', '1.0')

    def get_compliance_flags(self, obj):
        metadata = obj.policy_metadata or {}  # guard against null
        return metadata.get('compliance_flags', [])

    class Meta:
        model = PolicyDocument
        fields = [
            'id', 'policy_number', 'document_type',
            'state_code', 'effective_date', 'content_url',
            'metadata_version', 'compliance_flags',
            'created_at',
        ]
