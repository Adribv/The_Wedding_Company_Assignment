from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import org_routes, auth_routes
from app.db.mongo import close_mongo_connection
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Multi-tenant Organization Management Service with MongoDB",
        debug=settings.debug
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(org_routes.router)
    app.include_router(auth_routes.router)
    
    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting up Organization Management Service...")
        logger.info(f"MongoDB URL: {settings.mongodb_url}")
        logger.info(f"Master DB: {settings.mongodb_db_name}")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down...")
        await close_mongo_connection()
    
    @app.get("/", tags=["root"])
    async def root():
        return {
            "message": "Organization Management Service API",
            "version": settings.app_version,
            "docs": "/docs"
        }
    
    @app.get("/health", tags=["health"])
    async def health_check():
        return {"status": "healthy"}
    
    return app


# Create app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

