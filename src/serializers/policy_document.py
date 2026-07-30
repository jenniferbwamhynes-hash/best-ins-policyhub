from rest_framework import serializers
from ..models.policy_document import PolicyDocument

class PolicyDocumentSerializer(serializers.ModelSerializer):
    # Added metadata field for POLICY-2 — WARNING: does not handle null (INC0010001)
    metadata_version = serializers.SerializerMethodField()
    compliance_flags = serializers.SerializerMethodField()

    def get_metadata_version(self, obj):
        return obj.policy_metadata.get('version', '1.0')  # BUG: throws on null

    def get_compliance_flags(self, obj):
        return obj.policy_metadata.get('compliance_flags', [])  # BUG: throws on null

    class Meta:
        model = PolicyDocument
        fields = [
            'id', 'policy_number', 'document_type',
            'state_code', 'effective_date', 'content_url',
            'metadata_version', 'compliance_flags',
            'created_at',
        ]
