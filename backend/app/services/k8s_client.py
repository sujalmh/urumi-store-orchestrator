import logging
from time import sleep
from typing import List, cast

from kubernetes import client, config

logger = logging.getLogger("k8s_client")


class K8sClient:
    def __init__(self, kubeconfig_path: str | None = None):
        if kubeconfig_path:
            config.load_kube_config(config_file=kubeconfig_path)
        else:
            try:
                config.load_kube_config()
            except config.ConfigException:
                config.load_incluster_config()
        self.core = client.CoreV1Api()
        self.batch = client.BatchV1Api()

    def get_pod_status(self, namespace: str, label_selector: str) -> List[dict]:
        pods = self.core.list_namespaced_pod(namespace, label_selector=label_selector)
        results = []
        for pod in pods.items:
            ready = False
            if pod.status.container_statuses:
                ready = all(cs.ready for cs in pod.status.container_statuses)
            results.append({"name": pod.metadata.name, "ready": ready})
        return results

    def namespace_exists(self, namespace: str) -> bool:
        try:
            self.core.read_namespace(namespace)
            return True
        except client.ApiException as exc:
            if exc.status == 404:
                return False
            raise

    def ensure_namespace(self, namespace: str):
        if self.namespace_exists(namespace):
            return
        body = client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace))
        self.core.create_namespace(body)

    def delete_namespace(self, namespace: str):
        try:
            self.core.delete_namespace(namespace)
        except client.ApiException as exc:
            if exc.status == 404:
                return
            raise

    def wait_for_namespace_deletion(self, namespace: str, timeout: int = 600):
        waited = 0
        while waited < timeout:
            if not self.namespace_exists(namespace):
                return
            sleep(5)
            waited += 5
        raise TimeoutError(f"Namespace {namespace} deletion timed out")

    def wait_for_job_completion(self, namespace: str, job_name: str, timeout: int = 900, backoff_limit: int = 5):
        logger.info(f"wait_job_start: namespace={namespace}, job={job_name}")
        waited = 0
        seen_job = False
        last_status = None
        while waited < timeout:
            try:
                job = cast(client.V1Job, self.batch.read_namespaced_job(job_name, namespace))
                if not seen_job:
                    logger.info(f"wait_job_found: job={job_name}")
                seen_job = True
                status = job.status
                # Log status changes
                current_status = f"succeeded={getattr(status, 'succeeded', 0)}, failed={getattr(status, 'failed', 0)}"
                if current_status != last_status:
                    logger.info(f"wait_job_status: {current_status}, waited={waited}s")
                    last_status = current_status
                if status and status.succeeded and status.succeeded >= 1:
                    logger.info(f"wait_job_complete: job={job_name}, total_wait={waited}s")
                    return
                if status and status.failed and status.failed >= backoff_limit:
                    logger.error(f"wait_job_failed: job={job_name}, failed_count={status.failed}")
                    raise RuntimeError(f"Job {job_name} failed")
            except client.ApiException as exc:
                if exc.status == 404:
                    if seen_job:
                        logger.info(f"wait_job_deleted: job={job_name} was deleted after completion")
                        return
                    # Job not found - could be not created yet OR already completed and deleted
                    # If we've waited more than 180s, check if WordPress is ready as alternative signal
                    if waited > 180:
                        if self._is_wordpress_ready(namespace):
                            logger.info(f"wait_job_assumed_complete: job={job_name} not found but WordPress is ready, waited={waited}s")
                            return
                    if waited % 30 == 0:  # Log every 30 seconds while waiting for job to appear
                        logger.info(f"wait_job_not_found: job={job_name} not yet created, waited={waited}s")
                else:
                    logger.error(f"wait_job_api_error: {exc}")
                    raise
            sleep(10)
            waited += 10
        logger.error(f"wait_job_timeout: job={job_name}, timeout={timeout}s")
        raise TimeoutError(f"Job {job_name} timed out")

    def _is_wordpress_ready(self, namespace: str) -> bool:
        """Check if WordPress pod is ready as alternative completion signal."""
        try:
            pods = self.core.list_namespaced_pod(namespace, label_selector="app=wordpress")
            for pod in pods.items:
                if pod.status.phase == "Running":
                    # Check if container is ready
                    if pod.status.container_statuses:
                        for cs in pod.status.container_statuses:
                            if cs.ready:
                                return True
            return False
        except Exception as e:
            logger.warning(f"wordpress_ready_check_failed: {e}")
            return False
