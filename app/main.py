from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging import log_requests
from app.core.admin import create_default_admin
from app.api.routers import auth, user, book_service, booking, reviews
from app.db.session import get_db, engine
from app.db.base import Base

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BookIt API",
    description="""
    ## BookIt - Service Booking Platform API

    A production-ready REST API for a bookings platform where users can browse services, make bookings, and leave reviews.
    
    ### Features
    
    * **Authentication**: JWT-based authentication with role-based access control
    * **Services**: Browse and manage services (Admin can CRUD, users can view)
    * **Bookings**: Create, manage bookings with conflict detection
    * **Reviews**: Leave and manage reviews for completed bookings
    * **Admin Panel**: Administrative functions for managing the platform
    
    ### Authentication
    
    Most endpoints require authentication. To authenticate:
    1. Register a new account or login with existing credentials
    2. Use the returned access token in the Authorization header: `Bearer <token>`
    
    ### Roles
    
    * **User**: Can manage their own bookings and reviews
    * **Admin**: Can manage all services, bookings, and view all data
    """,
    version="1.0.0",
    contact={
        "name": "BookIt API Support",
        "email": "support@bookit.com",
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=[
        {
            "name": "auth",
            "description": "Authentication operations - register, login, refresh tokens"
        },
        {
            "name": "users", 
            "description": "User profile management"
        },
        {
            "name": "services",
            "description": "Service management - browse available services (public), manage services (admin only)"
        },
        {
            "name": "Bookings",
            "description": "Booking operations - create, view, modify bookings with conflict detection"
        },
        {
            "name": "reviews",
            "description": "Review management - create and manage reviews for completed bookings"
        }
    ]
)

# Add CORS middleware for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://bookit-api.onrender.com", "http://localhost:3000", "http://localhost:8080"],  # Update with your Render URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

# Add logging middleware
app.middleware("http")(log_requests)

# Include routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(book_service.router)
app.include_router(booking.router)
app.include_router(reviews.router)

@app.on_event("startup")
async def startup_event():
    """Create default admin user on startup if none exists."""
    create_default_admin()


@app.get("/", tags=["root"])
async def read_root():
    """
    Root endpoint - Welcome message and API information.
    """
    return {
        "message": "Welcome to BookIt API!",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }
