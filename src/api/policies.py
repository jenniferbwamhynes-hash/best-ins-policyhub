from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models.policy_document import PolicyDocument
from ..serializers.policy_document import PolicyDocumentSerializer

class PolicyDetailView(APIView):
    def get(self, request, policy_id):
        try:
            doc = PolicyDocument.objects.get(id=policy_id)
            serializer = PolicyDocumentSerializer(doc)
            return Response(serializer.data)
        except PolicyDocument.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
