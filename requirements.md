# Requirements Document

## Introduction

The Store Provisioning Platform is a multi-tenant SaaS system that enables users to provision and manage isolated WooCommerce stores on a Kubernetes cluster. Each store runs in its own namespace with dedicated WordPress, WooCommerce, and MySQL instances, providing complete isolation between tenants. The platform consists of a Next.js frontend for user interaction, a FastAPI backend for orchestration, and automated Kubernetes resource management using Helm charts.

## Glossary

- **Platform**: The Store Provisioning Platform system
- **User**: An authenticated person using the platform to manage stores
- **Store**: A WooCommerce instance with WordPress and MySQL running in an isolated Kubernetes namespace
- **Provisioning_Service**: The FastAPI backend service that orchestrates store creation and management
- **Dashboard**: The Next.js frontend application
- **Kubernetes_Cluster**: The k3s cluster hosting all stores
- **Namespace**: A Kubernetes namespace providing isolation for a single store
- **Helm_Chart**: The templated Kubernetes resource definitions for deploying a store
- **Tenant**: A user and their associated stores (tenant-per-namespace model)
- **Store_Status**: The current state of a store (Pending, Ready, Error, Deleting)
- **Resource_Quota**: Kubernetes limits on compute and storage resources per namespace
- **Ingress_Controller**: Traefik or Nginx handling external traffic routing
- **Cert_Manager**: Automated TLS certificate provisioning service
- **Background_Task**: Asynchronous job processing Helm operations
- **Admin_Credentials**: WordPress administrator username and password for a store

## Requirements

### Requirement 1: Store Creation

**User Story:** As a user, I want to request a new WooCommerce store through the web interface, so that I can quickly launch an online store without manual infrastructure setup.

#### Acceptance Criteria

1. WHEN a user submits a valid store creation request, THE Provisioning_Service SHALL create a new store record with status "Pending"
2. WHEN a store creation request is received, THE Provisioning_Service SHALL return HTTP 202 Accepted with a store identifier
3. WHEN a store creation request is submitted, THE Provisioning_Service SHALL enqueue a Background_Task to perform Helm deployment
4. WHEN the Background_Task executes, THE Provisioning_Service SHALL create a dedicated Namespace for the store
5. WHEN deploying store resources, THE Provisioning_Service SHALL use the Helm_Chart to create all required Kubernetes resources
6. WHEN a store creation request is re-submitted for an existing store, THE Provisioning_Service SHALL treat it as idempotent and either return the existing store or update it
7. WHEN store deployment completes successfully, THE Provisioning_Service SHALL update the Store_Status to "Ready"
8. WHEN store deployment fails, THE Provisioning_Service SHALL update the Store_Status to "Error" and log the failure reason

### Requirement 2: Kubernetes Resource Provisioning

**User Story:** As a platform operator, I want each store to run in complete isolation with proper resource limits, so that tenants cannot interfere with each other and resource usage is controlled.

#### Acceptance Criteria

1. WHEN a store is provisioned, THE Provisioning_Service SHALL create a unique Namespace named after the store identifier
2. WHEN creating a Namespace, THE Provisioning_Service SHALL apply a ResourceQuota limiting CPU, memory, and storage
3. WHEN creating a Namespace, THE Provisioning_Service SHALL apply a LimitRange defining default and maximum resource limits for containers
4. WHEN deploying a store, THE Provisioning_Service SHALL create a MySQL Deployment with a PersistentVolumeClaim of 20Gi
5. WHEN deploying a store, THE Provisioning_Service SHALL create a WordPress Deployment with a PersistentVolumeClaim of 30Gi for uploads
6. WHEN deploying a store, THE Provisioning_Service SHALL create ClusterIP Services for MySQL and WordPress
7. WHEN deploying a store, THE Provisioning_Service SHALL create Kubernetes Secrets containing database credentials and WordPress salts
8. WHEN deploying a store, THE Provisioning_Service SHALL create an Ingress resource with TLS configuration for the store domain
9. WHEN an Ingress is created, THE Cert_Manager SHALL automatically provision a Let's Encrypt TLS certificate
10. WHEN deploying a store, THE Provisioning_Service SHALL apply NetworkPolicies enforcing default-deny with intra-namespace-only communication
11. WHEN deploying a store, THE Provisioning_Service SHALL create RBAC resources with least-privilege access for the namespace

### Requirement 3: Domain Routing and TLS

**User Story:** As a user, I want my store to be accessible via a custom domain with HTTPS, so that customers can securely access my online store.

#### Acceptance Criteria

1. WHEN a user specifies a domain during store creation, THE Provisioning_Service SHALL configure the Ingress with that domain
2. WHEN an Ingress is created with a domain, THE Cert_Manager SHALL request a TLS certificate from Let's Encrypt
3. WHEN a TLS certificate is issued, THE Ingress_Controller SHALL serve the store over HTTPS
4. WHEN a store becomes ready, THE Platform SHALL provide the HTTPS URL to the user
5. WHEN HTTP requests are received, THE Ingress_Controller SHALL redirect them to HTTPS

### Requirement 4: Store Listing and Retrieval

**User Story:** As a user, I want to view all my stores and their current status, so that I can monitor my deployments and access store information.

#### Acceptance Criteria

1. WHEN a user requests their store list, THE Provisioning_Service SHALL return all stores owned by that user
2. WHEN returning store information, THE Provisioning_Service SHALL include store identifier, name, domain, and Store_Status
3. WHEN a user requests details for a specific store, THE Provisioning_Service SHALL return complete store information including Admin_Credentials
4. WHEN a user requests a store they do not own, THE Provisioning_Service SHALL return HTTP 403 Forbidden
5. WHEN a store is in "Ready" status, THE Provisioning_Service SHALL include the store URL and Admin_Credentials in the response

### Requirement 5: Store Deletion

**User Story:** As a user, I want to delete a store I no longer need, so that I can free up resources and stop incurring costs.

#### Acceptance Criteria

1. WHEN a user requests store deletion, THE Provisioning_Service SHALL update the Store_Status to "Deleting"
2. WHEN a deletion request is received, THE Provisioning_Service SHALL enqueue a Background_Task to perform cleanup
3. WHEN the deletion Background_Task executes, THE Provisioning_Service SHALL use Helm to uninstall the store release
4. WHEN uninstalling a store, THE Provisioning_Service SHALL delete all Kubernetes resources in the store's Namespace
5. WHEN all resources are deleted, THE Provisioning_Service SHALL delete the Namespace
6. WHEN namespace deletion completes, THE Provisioning_Service SHALL remove the store record from the database
7. WHEN a user requests deletion of a store they do not own, THE Provisioning_Service SHALL return HTTP 403 Forbidden

### Requirement 6: Store Health Monitoring

**User Story:** As a user, I want to check if my store is healthy and operational, so that I can quickly identify and address issues.

#### Acceptance Criteria

1. WHEN a user requests store health status, THE Provisioning_Service SHALL query the Kubernetes_Cluster for pod readiness
2. WHEN checking health, THE Provisioning_Service SHALL verify that WordPress and MySQL pods are running and ready
3. WHEN all pods are healthy, THE Provisioning_Service SHALL return a healthy status
4. WHEN any pod is unhealthy, THE Provisioning_Service SHALL return an unhealthy status with details
5. WHEN a store does not exist, THE Provisioning_Service SHALL return HTTP 404 Not Found

### Requirement 7: User Authentication and Authorization

**User Story:** As a platform operator, I want users to authenticate before accessing the API, so that only authorized users can manage stores.

#### Acceptance Criteria

1. WHEN a user makes an API request, THE Provisioning_Service SHALL validate the JWT token or API key
2. WHEN authentication fails, THE Provisioning_Service SHALL return HTTP 401 Unauthorized
3. WHEN a user attempts to access another user's store, THE Provisioning_Service SHALL return HTTP 403 Forbidden
4. WHEN a valid token is provided, THE Provisioning_Service SHALL extract the user identity for authorization checks
5. WHEN a token expires, THE Provisioning_Service SHALL reject the request and return HTTP 401 Unauthorized

### Requirement 8: User Quota Enforcement

**User Story:** As a platform operator, I want to limit the number of stores each user can create, so that resources are fairly distributed and abuse is prevented.

#### Acceptance Criteria

1. WHEN a user attempts to create a store, THE Provisioning_Service SHALL check the user's current store count
2. WHEN a user has reached their quota limit, THE Provisioning_Service SHALL reject the request with HTTP 429 Too Many Requests
3. WHEN a user is below their quota, THE Provisioning_Service SHALL allow store creation
4. WHEN a store is deleted, THE Provisioning_Service SHALL decrement the user's store count
5. THE Platform SHALL enforce a default quota of 5 stores per user

### Requirement 9: Rate Limiting

**User Story:** As a platform operator, I want to rate-limit store creation requests, so that the system is not overwhelmed by rapid provisioning attempts.

#### Acceptance Criteria

1. WHEN a user submits store creation requests, THE Provisioning_Service SHALL enforce a rate limit of 1 request per minute per user
2. WHEN a user exceeds the rate limit, THE Provisioning_Service SHALL return HTTP 429 Too Many Requests
3. WHEN the rate limit window expires, THE Provisioning_Service SHALL allow new requests
4. WHEN rate limiting is applied, THE Provisioning_Service SHALL include Retry-After header in the response

### Requirement 10: Dashboard Store List Display

**User Story:** As a user, I want to see all my stores in a dashboard with their current status, so that I can quickly understand the state of my deployments.

#### Acceptance Criteria

1. WHEN a user accesses the Dashboard, THE Dashboard SHALL display a list of all user's stores
2. WHEN displaying stores, THE Dashboard SHALL show store name, domain, and Store_Status for each store
3. WHEN a store is in "Pending" status, THE Dashboard SHALL display a loading indicator
4. WHEN a store is in "Ready" status, THE Dashboard SHALL display the store URL as a clickable link
5. WHEN a store is in "Error" status, THE Dashboard SHALL display an error indicator with details
6. WHEN the store list is empty, THE Dashboard SHALL display a message prompting the user to create their first store

### Requirement 11: Dashboard Store Creation Form

**User Story:** As a user, I want to fill out a form to create a new store, so that I can easily specify store configuration without technical knowledge.

#### Acceptance Criteria

1. WHEN a user accesses the create store form, THE Dashboard SHALL display input fields for store name and domain
2. WHEN a user submits the form with valid data, THE Dashboard SHALL send a POST request to the Provisioning_Service
3. WHEN the API returns success, THE Dashboard SHALL add the new store to the list with "Pending" status
4. WHEN the API returns an error, THE Dashboard SHALL display the error message to the user
5. WHEN form validation fails, THE Dashboard SHALL display validation errors without submitting the request
6. WHEN a user has reached their quota, THE Dashboard SHALL disable the create button and display a quota message

### Requirement 12: Real-Time Status Updates

**User Story:** As a user, I want to see store status updates in real-time, so that I know when my store is ready without manually refreshing.

#### Acceptance Criteria

1. WHEN a store is in "Pending" status, THE Dashboard SHALL poll the API every 5 seconds for status updates
2. WHEN a store status changes to "Ready", THE Dashboard SHALL update the display and stop polling
3. WHEN a store status changes to "Error", THE Dashboard SHALL update the display and stop polling
4. WHEN the user navigates away from the Dashboard, THE Dashboard SHALL stop all polling
5. WHEN polling encounters an error, THE Dashboard SHALL retry with exponential backoff

### Requirement 13: Store Credentials Display

**User Story:** As a user, I want to view my store's admin credentials when it's ready, so that I can log in and configure my WooCommerce store.

#### Acceptance Criteria

1. WHEN a store reaches "Ready" status, THE Dashboard SHALL display the WordPress admin URL
2. WHEN a user clicks to view credentials, THE Dashboard SHALL fetch and display the Admin_Credentials
3. WHEN displaying credentials, THE Dashboard SHALL provide a copy-to-clipboard button for the password
4. WHEN credentials are displayed, THE Dashboard SHALL show a security warning to change the password after first login
5. WHEN a store is not ready, THE Dashboard SHALL not display credential information

### Requirement 14: Container Security

**User Story:** As a platform operator, I want all containers to run with security best practices, so that the platform is protected from container escape and privilege escalation attacks.

#### Acceptance Criteria

1. WHEN deploying WordPress containers, THE Provisioning_Service SHALL configure them to run as non-root user (UID 1000)
2. WHEN deploying MySQL containers, THE Provisioning_Service SHALL configure them to run as non-root user (UID 999)
3. WHEN creating pods, THE Provisioning_Service SHALL apply Pod Security Admission restricted mode
4. WHEN configuring containers, THE Provisioning_Service SHALL set readOnlyRootFilesystem where possible
5. WHEN configuring containers, THE Provisioning_Service SHALL drop all capabilities except required ones
6. WHEN configuring containers, THE Provisioning_Service SHALL disable privilege escalation

### Requirement 15: Network Isolation

**User Story:** As a platform operator, I want network traffic between tenants to be blocked, so that stores cannot communicate with each other and tenant data remains isolated.

#### Acceptance Criteria

1. WHEN a Namespace is created, THE Provisioning_Service SHALL apply a default-deny NetworkPolicy
2. WHEN applying NetworkPolicies, THE Provisioning_Service SHALL allow intra-namespace communication between WordPress and MySQL
3. WHEN applying NetworkPolicies, THE Provisioning_Service SHALL allow ingress traffic from the Ingress_Controller to WordPress
4. WHEN applying NetworkPolicies, THE Provisioning_Service SHALL deny all traffic between different store namespaces
5. WHEN applying NetworkPolicies, THE Provisioning_Service SHALL allow egress to DNS and external services for WordPress

### Requirement 16: Secrets Management

**User Story:** As a platform operator, I want sensitive data like database passwords to be stored securely, so that credentials are not exposed in configuration files or logs.

#### Acceptance Criteria

1. WHEN creating a store, THE Provisioning_Service SHALL generate random database credentials
2. WHEN creating a store, THE Provisioning_Service SHALL generate random WordPress salts
3. WHEN storing credentials, THE Provisioning_Service SHALL create Kubernetes Secrets in the store's Namespace
4. WHEN configuring WordPress and MySQL, THE Provisioning_Service SHALL reference credentials from Secrets using environment variables
5. WHEN logging operations, THE Provisioning_Service SHALL never log secret values
6. WHEN returning store details, THE Provisioning_Service SHALL only include Admin_Credentials for authenticated store owners

### Requirement 17: Input Validation

**User Story:** As a platform operator, I want all API inputs to be validated, so that invalid or malicious data is rejected before processing.

#### Acceptance Criteria

1. WHEN receiving API requests, THE Provisioning_Service SHALL validate all inputs using Pydantic models
2. WHEN validation fails, THE Provisioning_Service SHALL return HTTP 422 Unprocessable Entity with detailed error messages
3. WHEN validating store names, THE Provisioning_Service SHALL enforce alphanumeric characters and hyphens only
4. WHEN validating domains, THE Provisioning_Service SHALL enforce valid DNS hostname format
5. WHEN validating domains, THE Provisioning_Service SHALL reject domains that are already in use
6. WHEN validating store identifiers, THE Provisioning_Service SHALL enforce UUID format

### Requirement 18: Audit Logging

**User Story:** As a platform operator, I want all store operations to be logged, so that I can audit user actions and troubleshoot issues.

#### Acceptance Criteria

1. WHEN a store is created, THE Provisioning_Service SHALL log the user identity, store identifier, and timestamp
2. WHEN a store is deleted, THE Provisioning_Service SHALL log the user identity, store identifier, and timestamp
3. WHEN authentication fails, THE Provisioning_Service SHALL log the attempted user identity and source IP
4. WHEN authorization fails, THE Provisioning_Service SHALL log the user identity and attempted resource
5. WHEN API errors occur, THE Provisioning_Service SHALL log the error details with request context
6. WHEN logging, THE Provisioning_Service SHALL include structured metadata for log aggregation

### Requirement 19: Metrics Collection

**User Story:** As a platform operator, I want to collect metrics on store provisioning and resource usage, so that I can monitor system health and capacity.

#### Acceptance Criteria

1. WHEN stores are provisioned, THE Provisioning_Service SHALL expose Prometheus metrics for provisioning duration
2. WHEN stores are provisioned, THE Provisioning_Service SHALL expose Prometheus metrics for success and failure counts
3. WHEN API requests are processed, THE Provisioning_Service SHALL expose Prometheus metrics for request latency and status codes
4. WHEN stores are running, THE Kubernetes_Cluster SHALL expose per-namespace metrics for CPU and memory usage
5. WHEN collecting metrics, THE Platform SHALL label metrics with namespace identifiers for per-tenant visibility

### Requirement 20: Log Aggregation

**User Story:** As a platform operator, I want logs from all stores to be centrally aggregated, so that I can troubleshoot issues and analyze system behavior.

#### Acceptance Criteria

1. WHEN containers emit logs, THE Platform SHALL collect them using Fluent Bit
2. WHEN collecting logs, THE Platform SHALL enrich log entries with namespace metadata
3. WHEN aggregating logs, THE Platform SHALL forward them to Loki or Elasticsearch
4. WHEN querying logs, THE Platform SHALL support filtering by namespace and store identifier
5. WHEN storing logs, THE Platform SHALL retain logs for at least 30 days

### Requirement 21: Health Probes

**User Story:** As a platform operator, I want WordPress and MySQL pods to have health probes, so that Kubernetes can automatically restart unhealthy containers.

#### Acceptance Criteria

1. WHEN deploying WordPress, THE Provisioning_Service SHALL configure readiness probes checking HTTP /wp-admin/install.php
2. WHEN deploying WordPress, THE Provisioning_Service SHALL configure liveness probes checking HTTP /wp-admin/install.php
3. WHEN deploying MySQL, THE Provisioning_Service SHALL configure readiness probes using mysqladmin ping
4. WHEN deploying MySQL, THE Provisioning_Service SHALL configure liveness probes using mysqladmin ping
5. WHEN a probe fails repeatedly, THE Kubernetes_Cluster SHALL restart the unhealthy container

### Requirement 22: Helm Chart Template

**User Story:** As a platform developer, I want a reusable Helm chart for store deployment, so that all stores are provisioned consistently with the same configuration structure.

#### Acceptance Criteria

1. WHEN the Helm_Chart is used, THE Helm_Chart SHALL create a Namespace resource
2. WHEN the Helm_Chart is used, THE Helm_Chart SHALL create ResourceQuota and LimitRange resources
3. WHEN the Helm_Chart is used, THE Helm_Chart SHALL create NetworkPolicy resources
4. WHEN the Helm_Chart is used, THE Helm_Chart SHALL create RBAC resources (ServiceAccount, Role, RoleBinding)
5. WHEN the Helm_Chart is used, THE Helm_Chart SHALL create Secret resources for database credentials and WordPress salts
6. WHEN the Helm_Chart is used, THE Helm_Chart SHALL create PersistentVolumeClaim resources for MySQL and WordPress
7. WHEN the Helm_Chart is used, THE Helm_Chart SHALL create Deployment resources for MySQL and WordPress
8. WHEN the Helm_Chart is used, THE Helm_Chart SHALL create Service resources for MySQL and WordPress
9. WHEN the Helm_Chart is used, THE Helm_Chart SHALL create an Ingress resource with TLS configuration
10. WHEN the Helm_Chart is used, THE Helm_Chart SHALL accept parameters via values.yaml for store name, domain, and resource limits
11. WHEN the Helm_Chart is upgraded, THE Helm_Chart SHALL support in-place updates without data loss
12. WHEN the Helm_Chart is rolled back, THE Helm_Chart SHALL restore the previous configuration

### Requirement 23: Background Task Processing

**User Story:** As a platform developer, I want Helm operations to run asynchronously, so that API requests return quickly and don't block on long-running operations.

#### Acceptance Criteria

1. WHEN a store creation request is received, THE Provisioning_Service SHALL enqueue a Background_Task and return immediately
2. WHEN a Background_Task is enqueued, THE Provisioning_Service SHALL persist the task state to the database
3. WHEN a Background_Task executes, THE Provisioning_Service SHALL update the store status based on task progress
4. WHEN a Background_Task fails, THE Provisioning_Service SHALL retry up to 3 times with exponential backoff
5. WHEN a Background_Task fails after all retries, THE Provisioning_Service SHALL mark the store as "Error" and log the failure
6. WHEN multiple Background_Tasks are queued, THE Provisioning_Service SHALL process them concurrently with a configurable worker pool

### Requirement 24: Database Persistence

**User Story:** As a platform developer, I want all store metadata to be persisted in a database, so that the system state is durable and survives service restarts.

#### Acceptance Criteria

1. WHEN a store is created, THE Provisioning_Service SHALL persist the store record to PostgreSQL
2. WHEN storing records, THE Provisioning_Service SHALL include store identifier, user identifier, name, domain, status, and timestamps
3. WHEN a store status changes, THE Provisioning_Service SHALL update the database record
4. WHEN a store is deleted, THE Provisioning_Service SHALL remove the database record
5. WHEN the Provisioning_Service starts, THE Provisioning_Service SHALL reconnect to the database and resume operations

### Requirement 25: Horizontal Scaling

**User Story:** As a platform operator, I want the FastAPI backend to scale horizontally, so that the system can handle increased load.

#### Acceptance Criteria

1. WHEN deploying the Provisioning_Service, THE Platform SHALL support running multiple replicas
2. WHEN multiple replicas are running, THE Provisioning_Service SHALL share state via the PostgreSQL database
3. WHEN multiple replicas are running, THE Provisioning_Service SHALL distribute Background_Tasks across workers
4. WHEN a replica fails, THE Platform SHALL route traffic to healthy replicas
5. WHEN load increases, THE Platform SHALL support adding more Provisioning_Service replicas without downtime

### Requirement 26: Store Auto-Scaling

**User Story:** As a user, I want my store to automatically scale under load, so that it can handle traffic spikes without manual intervention.

#### Acceptance Criteria

1. WHEN deploying a store, THE Provisioning_Service SHALL create a HorizontalPodAutoscaler for the WordPress Deployment
2. WHEN CPU usage exceeds 70%, THE HorizontalPodAutoscaler SHALL increase WordPress pod replicas
3. WHEN CPU usage drops below 30%, THE HorizontalPodAutoscaler SHALL decrease WordPress pod replicas
4. WHEN scaling, THE HorizontalPodAutoscaler SHALL maintain between 1 and 5 replicas
5. WHEN multiple WordPress pods are running, THE Service SHALL load-balance traffic across them

### Requirement 27: Idempotent Operations

**User Story:** As a platform developer, I want store creation to be idempotent, so that retrying failed operations doesn't create duplicate resources.

#### Acceptance Criteria

1. WHEN a store creation request is submitted for an existing store identifier, THE Provisioning_Service SHALL return the existing store information
2. WHEN Helm install is called for an existing release, THE Provisioning_Service SHALL treat it as an upgrade operation
3. WHEN creating Kubernetes resources, THE Provisioning_Service SHALL use declarative apply operations
4. WHEN a Background_Task is retried, THE Provisioning_Service SHALL check if resources already exist before creating them
5. WHEN a store is already in "Ready" status, THE Provisioning_Service SHALL not re-provision resources

### Requirement 28: Error Handling and User Feedback

**User Story:** As a user, I want clear error messages when operations fail, so that I understand what went wrong and how to fix it.

#### Acceptance Criteria

1. WHEN an API error occurs, THE Provisioning_Service SHALL return a structured error response with error code and message
2. WHEN validation fails, THE Provisioning_Service SHALL return specific field-level error messages
3. WHEN a store fails to provision, THE Dashboard SHALL display the error message to the user
4. WHEN quota limits are reached, THE Dashboard SHALL display a clear message explaining the limit
5. WHEN network errors occur, THE Dashboard SHALL display a user-friendly error message and retry option

### Requirement 29: Grafana Dashboards

**User Story:** As a platform operator, I want pre-built Grafana dashboards for monitoring stores, so that I can quickly visualize system health and resource usage.

#### Acceptance Criteria

1. WHEN Grafana is deployed, THE Platform SHALL include dashboards for per-namespace resource usage
2. WHEN viewing dashboards, THE Platform SHALL display CPU and memory usage per store
3. WHEN viewing dashboards, THE Platform SHALL display storage usage per store
4. WHEN viewing dashboards, THE Platform SHALL display pod health status per store
5. WHEN viewing dashboards, THE Platform SHALL display API request metrics for the Provisioning_Service

### Requirement 30: TLS Certificate Automation

**User Story:** As a platform operator, I want TLS certificates to be automatically provisioned and renewed, so that stores remain accessible over HTTPS without manual certificate management.

#### Acceptance Criteria

1. WHEN an Ingress is created with TLS configuration, THE Cert_Manager SHALL detect the certificate request
2. WHEN a certificate is requested, THE Cert_Manager SHALL complete the Let's Encrypt ACME challenge
3. WHEN a certificate is issued, THE Cert_Manager SHALL store it as a Kubernetes Secret
4. WHEN a certificate approaches expiration, THE Cert_Manager SHALL automatically renew it
5. WHEN certificate renewal fails, THE Cert_Manager SHALL retry and log the failure for operator attention
