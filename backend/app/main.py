from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from http import HTTPStatus

from app.schemas.store import ErrorResponse
from app.core.config import settings
from app.db.session import init_db

from app.api.router import api_router


app = FastAPI(title="Store Provisioning Platform")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.exception_handler(HTTPException)
def http_exception_handler(_: Request, exc: HTTPException):
    name = HTTPStatus(exc.status_code).phrase if exc.status_code in HTTPStatus._value2member_map_ else "Error"
    payload = ErrorResponse(error=name, detail=str(exc.detail))
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


@app.exception_handler(RequestValidationError)
def validation_exception_handler(_: Request, exc: RequestValidationError):
    field_errors: dict[str, list[str]] = {}
    for err in exc.errors():
        loc = err.get("loc", [])
        if len(loc) > 1:
            field = str(loc[1])
            field_errors.setdefault(field, []).append(err.get("msg", "Invalid value"))
    payload = ErrorResponse(
        error="Validation Error",
        detail="Invalid input data",
        field_errors=field_errors or None,
    )
    return JSONResponse(status_code=422, content=payload.model_dump())
