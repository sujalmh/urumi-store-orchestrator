import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_store_for_user, rate_limit_dependency
from app.core.config import settings
from app.db.session import get_db
from app.models.store import StoreORM
from app.models.user import UserORM
from app.schemas.store import CreateStoreRequest, HealthStatus, StoreDetailsResponse, StoreResponse, StoreStatus
from app.services.audit import log_audit
from app.services.k8s_client import K8sClient
from app.services.quotas import check_quota
from app.tasks.store_tasks import delete_store_task, provision_store_task


router = APIRouter(prefix="/stores", tags=["stores"])


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=StoreResponse,
    dependencies=[Depends(rate_limit_dependency("POST /stores", 1, 60))],
)
def create_store(
    request: CreateStoreRequest,
    req: Request,
    current_user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    slug = request.name
    domain = f"{slug}.{settings.public_ip}.{settings.base_domain}"
    if request.domain and request.domain != domain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Domain must be {domain} for nip.io routing",
        )

    if not check_quota(db, current_user.id, current_user.store_quota):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Quota exceeded")

    existing = db.query(StoreORM).filter(StoreORM.domain == domain).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Domain already in use")

    store_id = uuid.uuid4()
    store = StoreORM(
        id=store_id,
        user_id=current_user.id,
        name=slug,
        domain=domain,
        namespace=f"store-{store_id}",
        status=StoreStatus.PENDING.value,
        helm_release_name=f"store-{store_id}",
    )
    db.add(store)
    db.commit()
    db.refresh(store)

    provision_store_task.delay(str(store.id))

    log_audit(
        db,
        user_id=current_user.id,
        action="create_store",
        resource_type="store",
        resource_id=store.id,
        ip_address=req.client.host if req and req.client else None,
    )

    return store


@router.get("", response_model=list[StoreResponse])
def list_stores(
    current_user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stores = db.query(StoreORM).filter(StoreORM.user_id == current_user.id).all()
    return stores


@router.get("/{store_id}", response_model=StoreDetailsResponse)
def get_store(
    store: StoreORM = Depends(get_store_for_user),
):
    return store


@router.delete("/{store_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_store(
    req: Request,
    store: StoreORM = Depends(get_store_for_user),
    current_user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    store.status = StoreStatus.DELETING.value
    db.commit()

    delete_store_task.delay(str(store.id))

    log_audit(
        db,
        user_id=current_user.id,
        action="delete_store",
        resource_type="store",
        resource_id=store.id,
        ip_address=req.client.host if req and req.client else None,
    )

    return {"status": "deleting"}


@router.get("/{store_id}/health", response_model=HealthStatus)
def store_health(
    store: StoreORM = Depends(get_store_for_user),
):
    k8s = K8sClient()
    wordpress = k8s.get_pod_status(store.namespace, "app=wordpress")
    mysql = k8s.get_pod_status(store.namespace, "app=mysql")

    wordpress_ready = all(p["ready"] for p in wordpress) if wordpress else False
    mysql_ready = all(p["ready"] for p in mysql) if mysql else False
    healthy = wordpress_ready and mysql_ready

    return HealthStatus(
        healthy=healthy,
        wordpress_ready=wordpress_ready,
        mysql_ready=mysql_ready,
        details=None if healthy else "One or more pods not ready",
    )
