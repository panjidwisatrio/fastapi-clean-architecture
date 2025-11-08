from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, me, permission, user, role, otp
from app.core.logging import log_request, setup_logger
from app.core.init_db import init_db
from app.core.config import settings

app = FastAPI()

# Configure logging
logger = setup_logger("app")

logger.info(f"Application starting in {settings.ENVIRONMENT} environment")

# Add logging middleware
app.middleware("http")(lambda req, call_next: log_request(logger, req, call_next))

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database initialization on startup
@app.on_event("startup")
async def startup_db_client():
    logger.info("Initializing database on startup")
    init_db(logger)
    logger.info("Database initialization completed")

# Include API routers
app.include_router(auth.router)
app.include_router(me.router)
app.include_router(user.router)
app.include_router(role.router)
app.include_router(permission.router)
app.include_router(otp.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Clean Architecture API"}
