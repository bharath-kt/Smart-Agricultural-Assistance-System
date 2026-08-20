"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.db.base import async_engine, Base
from app.api.v1.endpoints import weather, market, disease, schemes, auth, profile, history, chat
from app.services.scheme_service import scheme_service
from app.db.base import AsyncSessionLocal


configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting up Smart Agriculture API")
    
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as db:
        await scheme_service.initialize_schemes(db)
    
    logger.info("Database initialized")
    yield
    
    logger.info("Shutting down Smart Agriculture API")


app = FastAPI(
    title=settings.APP_NAME,
    description="Production-ready backend for Smart Agriculture Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5176",
        "https://smart-agricultural-assistance-syste.vercel.app",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "1.0.0"
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Smart Agriculture API",
        "docs": "/docs",
        "version": "1.0.0"
    }


app.include_router(auth.router, prefix="/api/v1")
app.include_router(profile.router, prefix="/api/v1")
app.include_router(history.router, prefix="/api/v1")
app.include_router(weather.router, prefix="/api/v1")
app.include_router(market.router, prefix="/api/v1")
app.include_router(disease.router, prefix="/api/v1")
app.include_router(schemes.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")

# Direct aliases for top-level /api/v1/signup and /api/v1/register
@app.post("/api/v1/signup", include_in_schema=False)
@app.post("/api/v1/signup/", include_in_schema=False)
@app.post("/api/v1/register", include_in_schema=False)
@app.post("/api/v1/register/", include_in_schema=False)
async def api_v1_signup_alias(request: auth.SignupRequest, db=Depends(auth.get_db)):
    return await auth.auth_service.signup(db, request)

@app.post("/api/v1/login", include_in_schema=False)
@app.post("/api/v1/login/", include_in_schema=False)
async def api_v1_login_alias(request: auth.LoginRequest, db=Depends(auth.get_db)):
    return await auth.auth_service.login(db, request)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
