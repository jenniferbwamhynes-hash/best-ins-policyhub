from django.db import models
import uuid

class PolicyDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy_number = models.CharField(max_length=50, db_index=True)
    document_type = models.CharField(max_length=30)
    state_code = models.CharField(max_length=2, db_index=True)
    effective_date = models.DateField()
    content_url = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'policy_documents'
        indexes = [
            models.Index(fields=['policy_number', 'document_type']),
        ]
