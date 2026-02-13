#!/usr/bin/env sh
set -e

if [ -n "${KUBERNETES_SERVICE_HOST:-}" ] && [ -f /var/run/secrets/kubernetes.io/serviceaccount/token ]; then
  TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
  CA_CERT=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
  SERVER="https://${KUBERNETES_SERVICE_HOST}:${KUBERNETES_SERVICE_PORT}"

  cat > /tmp/kubeconfig <<EOF
apiVersion: v1
kind: Config
clusters:
- cluster:
    certificate-authority: ${CA_CERT}
    server: ${SERVER}
  name: in-cluster
contexts:
- context:
    cluster: in-cluster
    user: in-cluster-user
  name: in-cluster
current-context: in-cluster
users:
- name: in-cluster-user
  user:
    token: ${TOKEN}
EOF

  export KUBECONFIG=/tmp/kubeconfig
fi

exec "$@"
