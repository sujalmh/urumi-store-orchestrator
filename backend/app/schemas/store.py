from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StoreStatus(str, Enum):
    PENDING = "Pending"
    READY = "Ready"
    ERROR = "Error"
    DELETING = "Deleting"


class CreateStoreRequest(BaseModel):
    name: str = Field(min_length=3, max_length=63, pattern=r"^[a-z0-9-]+$")
    domain: str = Field(pattern=r"^[a-z0-9.-]+\.[a-z]{2,}$")


class StoreResponse(BaseModel):
    id: UUID
    name: str
    domain: str
    status: StoreStatus
    created_at: datetime
    url: Optional[str] = None

    @staticmethod
    def _scheme(domain: str) -> str:
        if domain.endswith(".localtest.me") or domain.endswith(".localhost"):
            return "http"
        return "https"

    @model_validator(mode="after")
    def set_url(self):
        if self.status == StoreStatus.READY:
            self.url = f"{self._scheme(self.domain)}://{self.domain}"
        return self

    model_config = ConfigDict(from_attributes=True)


class StoreDetailsResponse(StoreResponse):
    admin_url: Optional[str] = None
    admin_username: Optional[str] = None
    admin_password: Optional[str] = None

    @model_validator(mode="after")
    def set_admin_url(self):
        if self.status == StoreStatus.READY:
            scheme = self._scheme(self.domain)
            self.admin_url = f"{scheme}://{self.domain}/wp-admin"
        return self


class HealthStatus(BaseModel):
    healthy: bool
    wordpress_ready: bool
    mysql_ready: bool
    details: Optional[str] = None


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    field_errors: Optional[Dict[str, List[str]]] = None
