from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.services import review as review_service
from app.services.auth import get_current_user
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate
from uuid import UUID
from app.db.models import User

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("/", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
def create_review(
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return review_service.create_review(db, review, current_user)

@router.get("/service/{service_id}/reviews", response_model=List[ReviewRead])
def get_service_reviews(service_id: UUID, db: Session = Depends(get_db)):
    return review_service.get_service_reviews(db, service_id)

@router.patch("/{review_id}", response_model=ReviewRead)
def update_review(
    review_id: UUID,
    review_in: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return review_service.update_review(db, review_id, review_in, current_user)

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    review_service.delete_review(db, str(review_id), current_user)
    return None