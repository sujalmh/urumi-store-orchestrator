# Store Provisioning Platform

Provision isolated WooCommerce stores on Kubernetes with a FastAPI backend, Celery workers, Helm charts, and a Next.js dashboard.

## Live Demo

- **Frontend UI**: https://frontend-henna-mu-66.vercel.app/
- **Backend**: Deployed on Google Kubernetes Engine (GKE)

## What This Project Does

- Create, provision, and delete WooCommerce stores per tenant
- Enforce Kubernetes isolation via namespaces, RBAC, quotas, PVCs, and NetworkPolicies
- Automate WooCommerce installation, COD payment enablement, and sample product creation
- Provide a web UI for store lifecycle management

## Architecture Overview

```mermaid
flowchart LR
  UI[Next.js Dashboard] -->|REST| API[FastAPI]
  API -->|tasks| CELERY[Celery Workers]
  CELERY -->|helm install/uninstall| HELM[Helm Chart]
  HELM -->|K8s resources| K8S[Kubernetes]
  K8S -->|WordPress + MySQL| STORE[WooCommerce Store]
  API --> DB[(PostgreSQL)]
  CELERY --> REDIS[(Redis)]
```

## Provisioning Flow

```mermaid
sequenceDiagram
  autonumber
  participant User
  participant UI
  participant API
  participant Worker
  participant K8s

  User->>UI: Create store
  UI->>API: POST /stores
  API->>Worker: enqueue provision task
  Worker->>K8s: helm upgrade --install
  K8s-->>Worker: WordPress + MySQL ready
  Worker->>K8s: WooCommerce install job
  K8s-->>Worker: Job complete
  Worker->>API: mark store Ready
  API-->>UI: status Ready
```

## Main Components

- Backend API: `backend/`
  - FastAPI, SQLAlchemy, JWT auth
  - Store lifecycle endpoints
  - Quotas and rate limiting
- Background Workers: `backend/app/tasks/`
  - Celery + Redis
  - Provision and deletion tasks
- Helm Chart: `helm/woocommerce-store/`
  - WordPress + MySQL
  - RBAC, quotas, PVCs, NetworkPolicies
  - WooCommerce post-install job
- Frontend: `frontend/`
  - Next.js dashboard for store management

## Quick Start

### 1) Requirements

- Python 3.12
- Node.js + npm
- Redis
- PostgreSQL
- Helm
- Kubernetes (GKE / k3d / k3s)

### 2) Backend + Workers

```bash
bash scripts/start-all.sh
```

### 3) Frontend

```bash
START_FRONTEND=1 bash scripts/start-all.sh
```

## Deployment Details (Submission)

### Live Endpoints

- Frontend (Vercel): https://frontend-henna-mu-66.vercel.app/
- Backend API (GKE + Ingress): http://api.34.47.223.43.nip.io

### Store URL Pattern

Stores are routed via nip.io (HTTP only):

```
http://<store-slug>.34.47.223.43.nip.io
```

### GKE Deployment Summary

- Cluster: `urumi-gke` (asia-south1-a)
- Ingress: nginx (LoadBalancer IP `34.47.223.43`)
- Platform namespace: `platform`
- Backend image: `asia-south1-docker.pkg.dev/urumi-487318/urumi/backend:latest`
- Data layer: Postgres + Redis in-cluster (StatefulSet/Deployment)

### Vercel Setup

Vercel is configured to proxy API calls to the HTTP backend (avoids mixed-content issues):

- Frontend calls: `/api/proxy/*`
- Proxy target env: `API_TARGET=http://api.34.47.223.43.nip.io`

### Platform Env (GKE)

Set via `platform-config` ConfigMap and `platform-secrets` Secret:

- `APP_PUBLIC_IP=34.47.223.43`
- `APP_BASE_DOMAIN=nip.io`
- `APP_VALUES_PROFILE=prod`
- `APP_TLS_ENABLED=false`
- `APP_INGRESS_CLASS_NAME=nginx`

### TLS Later (Optional)

If a real domain is available, enable TLS using cert-manager and switch
store URLs to `https://<slug>.<domain>`.

## API Surface (Core)

- `POST /auth/register`
- `POST /auth/login`
- `POST /stores`
- `GET /stores`
- `GET /stores/{store_id}`
- `DELETE /stores/{store_id}`

## Status Model

Stores transition through:

- Pending → Provisioning → Ready
- Pending → Error
- Deleting → (removed)

## Operational Notes

- Helm chart path is resolved to an absolute path before install
- WooCommerce install job uses internal service URL for REST calls
- COD is enabled and sample products are seeded

## Useful Commands

```bash
# Tail logs
tail -f /tmp/urumi/uvicorn.log
tail -f /tmp/urumi/celery.log

# Check tenant namespace
kubectl get ns | grep store-
kubectl get pods -n <store-namespace>
```

## Directory Index

- `backend/` FastAPI API, Celery tasks, DB models
- `frontend/` Next.js dashboard
- `helm/` Helm chart for tenant infrastructure
- `scripts/` helper scripts (start/cleanup)
- `documentation.md` project notes

## Screenshots

### Store Provisioning Status

![Provisioning Store](screenshots/provisioning-store.png)
*Store in provisioning state*

![Ready Store](screenshots/ready-store.png)
*Store ready with access URL*

### Store Actions

![Delete Store](screenshots/delete-store.png)
*Deleting a store*

### WooCommerce Shop

![WooCommerce Shop](screenshots/woocommerce-shop.png)
*Live WooCommerce storefront*
