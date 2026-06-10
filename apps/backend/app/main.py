from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.v1.router import router as v1_router
from app.core.logging import configure_logging
from app.middleware.rate_limit import RateLimitMiddleware

configure_logging()

app = FastAPI(title="CrateKey API")
app.add_middleware(RateLimitMiddleware)
app.include_router(v1_router)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    # Errors follow { error, code } — see CLAUDE.md API conventions
    return JSONResponse(status_code=422, content={"error": str(exc), "code": "validation_error"})


@app.exception_handler(Exception)
async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"error": "Internal server error", "code": "internal_error"})


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
