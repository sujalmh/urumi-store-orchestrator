from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/provisioning"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "dev-secret"
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 60
    kubeconfig_path: str | None = None
    helm_chart_path: str = str(BASE_DIR / "helm" / "woocommerce-store")
    
    @property
    def resolved_helm_chart_path(self) -> str:
        path = Path(self.helm_chart_path)
        if not path.is_absolute():
            path = BASE_DIR / path
        return str(path.resolve())
    storage_class_name: str = "local-path"
    tls_enabled: bool = False
    public_ip: str = "127.0.0.1"
    base_domain: str = "nip.io"
    values_profile: str = "local"
    ingress_class_name: str = "traefik"
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_prefix="APP_", case_sensitive=False, env_file=".env")


settings = Settings()
