from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.config import settings
from app.db.db import initialize_pool, shutdown
from app.routes import flows, health
from app.utils.logging import LogMiddleware


@asynccontextmanager
async def lifespan(_: FastAPI):
    await initialize_pool()
    yield
    await shutdown()


app = FastAPI(debug=settings.DEBUG, lifespan=lifespan)

# Routers
app.include_router(health.router)
app.include_router(flows.router)

# Middleware
app.add_middleware(LogMiddleware)


@app.exception_handler(ValidationError)
async def validation_exception_handler(_: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors()}),
    )
