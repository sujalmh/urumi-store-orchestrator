# MVP Implementation Plan: Store Provisioning Platform

## Scope

The MVP delivers a working end-to-end store lifecycle: create, list, get details, health check, and delete. It includes tenant isolation, Helm-based provisioning, basic auth, quotas/rate limits, TLS via cert-manager, and a usable dashboard. Property-based tests and advanced observability are deferred.

## In Scope (MVP)

### Foundation
- Project structure for FastAPI + Next.js
- Local dev setup: PostgreSQL, Redis (task queue), k3s + Helm

### Backend Core
- SQLAlchemy models: users, stores, audit_logs, rate_limits
- Pydantic models with validation and structured error responses
- JWT auth and store ownership authorization
- Quota enforcement and rate limiting

### Provisioning Engine
- Kubernetes client wrapper
- Helm client wrapper
- Background tasks: provision_store_task, delete_store_task
- Idempotent behavior for retries and Helm releases

### Helm Chart
- Namespace, ResourceQuota, LimitRange
- RBAC (ServiceAccount, Role, RoleBinding)
- Secrets, PVCs, Deployments, Services
- Ingress with TLS annotations
- NetworkPolicies for isolation
- Health probes for WordPress/MySQL

### API Surface
- POST /stores, GET /stores, GET /stores/{id}, DELETE /stores/{id}
- GET /stores/{id}/health
- Domain uniqueness checks and validation

### Frontend
- Auth screens (login/register)
- Store list page with polling for pending stores
- Create store form with validation and quota messaging
- Store details modal with credentials + copy action

## Deferred (Post-MVP)

- Property-based tests (all optional tasks marked with `*` in tasks.md)
- Full observability stack (Prometheus/Grafana dashboards, Fluent Bit log aggregation)
- Advanced security hardening (Pod Security Admission enforcement details, secret rotation)
- Performance/load testing and autoscaling validation
- Certificate auto-renewal monitoring and advanced alerting

## MVP Phase Order

1. Foundation setup
2. Core backend models and auth
3. Helm chart templates and isolation policies
4. Background task queue and provisioning tasks
5. Store CRUD endpoints + health check
6. Frontend dashboard + API client
7. Manual integration test in dev cluster

## MVP Exit Criteria

- User can create a store and receive 202 with Pending status
- Background task provisions a store and updates status to Ready
- Store is reachable at HTTPS domain with TLS
- Dashboard updates status without manual refresh
- Store deletion cleans up all resources and DB record
- Quota and rate limit errors are surfaced cleanly in UI
