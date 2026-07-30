"""
Regression tests for INC0010001 — null policy_metadata handling.
These tests must pass before any deploy that touches PolicyDocumentSerializer.
"""
import pytest
from unittest.mock import MagicMock
from src.serializers.policy_document import PolicyDocumentSerializer

def test_serializer_handles_null_metadata():
    """Regression: INC0010001 — serializer must not throw on null metadata"""
    doc = MagicMock()
    doc.policy_metadata = None
    s = PolicyDocumentSerializer(doc)
    assert s.data['metadata_version'] == '1.0'
    assert s.data['compliance_flags'] == []

def test_serializer_reads_populated_metadata():
    doc = MagicMock()
    doc.policy_metadata = {'version': '2.0', 'compliance_flags': ['IL-001', 'IL-002']}
    s = PolicyDocumentSerializer(doc)
    assert s.data['metadata_version'] == '2.0'
    assert 'IL-001' in s.data['compliance_flags']
