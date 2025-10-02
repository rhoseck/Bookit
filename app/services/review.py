from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models import Review, Booking, Service, User
from uuid import UUID
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewRead
from app.repositories import review_repo

def create_review(db: Session, review: ReviewCreate, current_user: User) -> ReviewRead:
    booking = db.query(Booking).filter(Booking.id == str(review.booking_id)).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to review this booking")
    if booking.status != "completed":
        raise HTTPException(status_code=400, detail="Can only review completed bookings")
    if db.query(Review).filter(Review.booking_id == booking.id).first():
        raise HTTPException(status_code=400, detail="Booking already reviewed")
    if not (1 <= review.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    db_review = review_repo.create_review(db, review, current_user.id)
    db_review.booking_id = booking.id
    db.commit()
    db.refresh(db_review)
    return ReviewRead.from_orm(db_review)

def get_service_reviews(db: Session, service_id: UUID) -> List[ReviewRead]:
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return review_repo.get_service_reviews(db, str(service.id))

def update_review(db: Session, review_id: str, review_in: ReviewUpdate, current_user: User) -> ReviewRead:
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if review_in.rating and not (1 <= review_in.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    review = review_repo.update_review(db, review_id, review_in)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    db.refresh(review)
    return ReviewRead.from_orm(review)

def delete_review(db: Session, review_id: str, current_user: User) -> bool:
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    review_repo.delete_review(db, review_id)
    return True