FROM python:3.12-slim

ARG HELM_VERSION=v3.15.4

RUN apt-get update \
  && apt-get install -y --no-install-recommends curl ca-certificates \
  && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL "https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz" \
  | tar -xz -C /tmp \
  && mv /tmp/linux-amd64/helm /usr/local/bin/helm \
  && rm -rf /tmp/linux-amd64

WORKDIR /app

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend/app /app/app
COPY helm /app/helm
COPY backend/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENV PYTHONUNBUFFERED=1
ENV APP_HELM_CHART_PATH=/app/helm/woocommerce-store

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
