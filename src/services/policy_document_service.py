import boto3
from ..models.policy_document import PolicyDocument

class PolicyDocumentService:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.bucket = 'best-ins-policy-docs'

    def generate(self, policy_number, document_type, state_code, effective_date):
        # Generate document content
        content = self._render_template(document_type, state_code)
        url = self._upload_to_s3(policy_number, document_type, content)

        doc = PolicyDocument.objects.create(
            policy_number=policy_number,
            document_type=document_type,
            state_code=state_code,
            effective_date=effective_date,
            content_url=url,
        )
        return doc

    def _render_template(self, document_type, state_code):
        # Template rendering logic
        pass

    def _upload_to_s3(self, policy_number, document_type, content):
        key = f"policies/{policy_number}/{document_type}.pdf"
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=content)
        return f"s3://{self.bucket}/{key}"
