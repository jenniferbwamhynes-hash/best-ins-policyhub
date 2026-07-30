# PolicyHub

Core policy management system for Best Insurance. Handles policy issuance,
endorsements, renewals, and compliance document generation.

## Stack
- Python 3.11 / Django 4.2
- PostgreSQL 15
- Celery + Redis (async tasks)
- REST API consumed by AgentPortal and CustomerAPI

## Key Services
- `PolicyDocumentService` — document generation and storage
- `PolicySerializer` — API serialization layer
- `ComplianceService` — state-mandated disclosure injection
