import copy
import json
import logging
import secrets
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
import yaml
from typing import Any, cast

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal, init_db
from app.models.store import StoreORM
from app.schemas.store import StoreStatus
from app.services.helm_client import HelmClient
from app.services.k8s_client import K8sClient
from app.tasks.celery_app import celery_app


logger = logging.getLogger("store_tasks")


def _random_string(length: int) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _deep_merge(base: dict, override: dict) -> dict:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _load_base_values() -> dict:
    chart_path = Path(settings.resolved_helm_chart_path)
    profile = settings.values_profile
    candidate = chart_path / f"values-{profile}.yaml"
    fallback = chart_path / "values.yaml"

    values_path = candidate if candidate.exists() else fallback
    with values_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _build_values(store: StoreORM) -> dict:
    mysql_password = _random_string(32)
    root_password = _random_string(32)
    admin_password = _random_string(32)
    salts = {
        "authKey": _random_string(64),
        "secureAuthKey": _random_string(64),
        "loggedInKey": _random_string(64),
        "nonceKey": _random_string(64),
        "authSalt": _random_string(64),
        "secureAuthSalt": _random_string(64),
        "loggedInSalt": _random_string(64),
        "nonceSalt": _random_string(64),
    }

    tls_enabled = settings.tls_enabled
    if store.domain.endswith(".localtest.me") or store.domain.endswith(".localhost"):
        tls_enabled = False
    if store.domain.endswith(".nip.io") or store.domain.endswith(".sslip.io"):
        tls_enabled = False
    scheme = "https" if tls_enabled else "http"

    dynamic_values = {
        "storeName": store.name,
        "storeId": str(store.id),
        "domain": store.domain,
        "namespace": {"name": store.namespace},
        "mysql": {
            "rootPassword": root_password,
            "database": "woocommerce",
            "user": "woocommerce",
            "password": mysql_password,
        },
        "wordpress": {
            "adminUser": "admin",
            "adminPassword": admin_password,
            "adminEmail": "admin@example.com",
            "siteTitle": store.name,
            "siteUrl": f"{scheme}://{store.domain}",
            "salts": salts,
        },
        "ingress": {
            "className": settings.ingress_class_name,
            "tls": {"enabled": tls_enabled},
        },
    }

    base_values = _load_base_values()
    return _deep_merge(base_values, dynamic_values)


def _write_values(values: dict) -> str:
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tmp:
        json.dump(values, tmp)
        return tmp.name


def _get_db() -> Session:
    return SessionLocal()


@celery_app.task(bind=True, max_retries=3)
def provision_store_task(self, store_id: str):
    db = _get_db()
    try:
        logger.info("provision_store.start", extra={"store_id": store_id})
        init_db()
        store = db.query(StoreORM).filter(StoreORM.id == store_id).first()
        if not store:
            logger.info("provision_store.missing", extra={"store_id": store_id})
            return
        store = cast(Any, store)
        if store.status == StoreStatus.READY.value:
            logger.info("provision_store.already_ready", extra={"store_id": store_id})
            return

        if not store.namespace:
            store.namespace = f"store-{store.id}"
        if not store.helm_release_name:
            store.helm_release_name = f"store-{store.id}"
        db.commit()

        values = _build_values(store)
        values_path = _write_values(values)

        helm = HelmClient()
        k8s = K8sClient(settings.kubeconfig_path)
        logger.info("provision_store.ensure_namespace", extra={"namespace": store.namespace})
        k8s.ensure_namespace(str(store.namespace))
        resolved_chart_path = settings.resolved_helm_chart_path
        logger.info("provision_store.helm_install_start", extra={"release": store.helm_release_name, "chart": resolved_chart_path, "namespace": store.namespace})
        try:
            helm.install(str(store.helm_release_name), resolved_chart_path, str(store.namespace), values_path)
            logger.info("provision_store.helm_install_complete", extra={"release": store.helm_release_name})
        except Exception as helm_err:
            logger.error("provision_store.helm_install_failed", extra={"release": store.helm_release_name, "error": str(helm_err)})
            raise

        logger.info("provision_store.wait_job_start", extra={"job": "woocommerce-install", "namespace": store.namespace})
        try:
            k8s.wait_for_job_completion(store.namespace, "woocommerce-install", timeout=900, backoff_limit=5)
            logger.info("provision_store.wait_job_complete", extra={"job": "woocommerce-install"})
        except Exception as job_err:
            logger.error("provision_store.wait_job_failed", extra={"job": "woocommerce-install", "error": str(job_err)})
            raise

        deadline = time.time() + 600
        while True:
            wordpress = k8s.get_pod_status(str(store.namespace), "app=wordpress")
            mysql = k8s.get_pod_status(str(store.namespace), "app=mysql")
            ready = wordpress and mysql and all(p["ready"] for p in wordpress + mysql)
            if ready:
                break
            if time.time() >= deadline:
                raise RuntimeError("Pods not ready")
            time.sleep(10)

        store.status = StoreStatus.READY.value
        store.admin_username = "admin"
        store.admin_password = values["wordpress"]["adminPassword"]
        store.ready_at = datetime.now(timezone.utc)
        db.commit()
        logger.info("provision_store.ready", extra={"store_id": store_id})
    except Exception as exc:
        db.rollback()
        logger.exception("provision_store.error", extra={"store_id": store_id})
        try:
            self.retry(exc=exc)
        except Exception:
            error_db = _get_db()
            try:
                store = error_db.query(StoreORM).filter(StoreORM.id == store_id).first()
                if store:
                    store = cast(Any, store)
                    store.status = StoreStatus.ERROR.value
                    store.error_message = str(exc)
                    error_db.commit()
            finally:
                error_db.close()
            raise
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def delete_store_task(self, store_id: str):
    db = _get_db()
    try:
        logger.info("delete_store.start", extra={"store_id": store_id})
        init_db()
        store = db.query(StoreORM).filter(StoreORM.id == store_id).first()
        if not store:
            logger.info("delete_store.missing", extra={"store_id": store_id})
            return
        store = cast(Any, store)

        helm = HelmClient()
        logger.info("delete_store.helm_uninstall", extra={"release": store.helm_release_name})
        helm.uninstall(str(store.helm_release_name), str(store.namespace))

        k8s = K8sClient(settings.kubeconfig_path)
        logger.info("delete_store.delete_namespace", extra={"namespace": store.namespace})
        k8s.delete_namespace(str(store.namespace))
        logger.info("delete_store.wait_namespace", extra={"namespace": store.namespace})
        k8s.wait_for_namespace_deletion(str(store.namespace))

        db.delete(store)
        db.commit()
        logger.info("delete_store.done", extra={"store_id": store_id})
    except Exception as exc:
        db.rollback()
        logger.exception("delete_store.error", extra={"store_id": store_id})
        try:
            self.retry(exc=exc)
        except Exception:
            raise
    finally:
        db.close()
