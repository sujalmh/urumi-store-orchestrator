#!/bin/bash
# cleanup.sh - Clean all store data from Redis, Helm, K8s, and PostgreSQL

set -e

echo "=== Cleaning up all store data ==="

# 1. Flush Redis
echo "Flushing Redis..."
redis-cli FLUSHDB
echo "✓ Redis flushed"

# 2. Uninstall Helm releases
echo "Uninstalling Helm releases..."
helm list -A -q | grep '^store-' | while read release; do
    ns=$(helm list -A | grep "^${release}\s" | awk '{print $2}')
    if [ -n "$ns" ]; then
        helm uninstall "$release" -n "$ns" 2>/dev/null || true
        echo "✓ Uninstalled Helm release: $release"
    fi
done

# 3. Delete K8s namespaces
echo "Deleting Kubernetes namespaces..."
kubectl get ns -o name | grep '^namespace/store-' | while read ns; do
    kubectl delete "$ns" --wait=false 2>/dev/null || true
    echo "✓ Deleted namespace: $ns"
done

# 4. Clean PostgreSQL
echo "Cleaning PostgreSQL..."
PGPASSWORD=postgres psql -h 127.0.0.1 -p 5432 -U postgres -d provisioning -c "
    DELETE FROM stores;
    DELETE FROM audit_logs WHERE resource_type='store';
" 2>/dev/null || echo "⚠ PostgreSQL cleanup may have failed"
echo "✓ PostgreSQL cleaned"

# 5. Clean up Celery results (if any)
echo "Cleaning Celery results..."
redis-cli DEL 'celery-task-meta-*' 2>/dev/null || true
echo "✓ Celery results cleaned"

echo ""
echo "=== Cleanup complete ==="
echo "Verification:"
echo "- Redis keys: $(redis-cli DBSIZE)"
echo "- Helm releases: $(helm list -A -q | grep -c '^store-' || echo 0)"
echo "- K8s namespaces: $(kubectl get ns -o name | grep -c 'namespace/store-' || echo 0)"
echo "- PostgreSQL stores: $(PGPASSWORD=postgres psql -h 127.0.0.1 -p 5432 -U postgres -d provisioning -t -c "SELECT COUNT(*) FROM stores;" 2>/dev/null | tr -d ' ')"
