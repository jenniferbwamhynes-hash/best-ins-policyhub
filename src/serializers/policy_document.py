from rest_framework import serializers
from ..models.policy_document import PolicyDocument

class PolicyDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyDocument
        fields = [
            'id', 'policy_number', 'document_type',
            'state_code', 'effective_date', 'content_url',
            'created_at',
        ]
