from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.book_service import ServiceCreate, ServiceRead, ServiceUpdate
from app.schemas.user import UserRole
from app.services import book_service
from app.services.security import require_admin
from app.db.models import User
from app.services import review as review_service
from app.schemas.review import ReviewRead
from uuid import UUID

router = APIRouter(prefix="/services", tags=["services"])

@router.post("/", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
def create_service(
    service_in: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a new service (Admin only)."""
    return book_service.create_service(db, service_in)

@router.get("/", response_model=list[ServiceRead])
def list_services(
    q: str | None = None,
    price_min: float | None = None,
    price_max: float | None = None,
    active: bool | None = None,
    db: Session = Depends(get_db)
):
    """List all available services with optional filters."""
    return book_service.get_services(db, q, price_min, price_max, active)

@router.get("/{service_id}", response_model=ServiceRead)
def get_service(service_id: UUID, db: Session = Depends(get_db)):
    """Get a single service by ID."""
    service = book_service.get_service(db, service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return service

@router.patch("/{service_id}", response_model=ServiceRead)
def update_service(
    service_id: UUID,  # Changed from int to UUID
    service_in: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update an existing service (Admin only)."""
    service = book_service.update_service(db, service_id, service_in)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return service

@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: UUID,  # Changed from int to UUID
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete a service (Admin only)."""
    ok = book_service.delete_service(db, service_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

@router.get("/{service_id}/reviews", response_model=list[ReviewRead])
def get_service_reviews(
    service_id: UUID,
    db: Session = Depends(get_db)
):
    """Get reviews for a service by its ID."""
    return review_service.get_service_reviews(db, service_id)