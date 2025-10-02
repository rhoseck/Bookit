from sqlalchemy.orm import Session, joinedload
from app.db.models import Review, Booking
from app.schemas.review import ReviewCreate, ReviewUpdate
from typing import List

def create_review(db: Session, review: ReviewCreate, user_id: str) -> Review:
    db_review = Review(
        booking_id=review.booking_id,
        user_id=user_id,
        rating=review.rating,
        comment=review.comment
    )
    db.add(db_review)
    db.commit()
    
    # Reload with relationships
    db_review = (
        db.query(Review)
        .options(joinedload(Review.booking).joinedload(Booking.service))
        .filter(Review.id == db_review.id)
        .first()
    )
    
    # Ensure service is assigned from the booking
    if db_review.booking and db_review.booking.service:
        db_review.service = db_review.booking.service
    
    return db_review
    return db_review

def get_service_reviews(db: Session, service_id: str) -> List[Review]:
    reviews = (
        db.query(Review)
        .join(Review.booking)
        .options(joinedload(Review.booking).joinedload(Booking.service))
        .filter(Booking.service_id == service_id)
        .all()
    )
    
    # Ensure service is assigned from the booking
    for review in reviews:
        if review.booking and review.booking.service:
            review.service = review.booking.service
    
    return reviews

def update_review(db: Session, review_id: str, review_in: ReviewUpdate) -> Review | None:
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        return None
    for field, value in review_in.dict(exclude_unset=True).items():
        setattr(review, field, value)
    db.commit()
    db.refresh(review)
    return review

def delete_review(db: Session, review_id: str) -> bool:
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        return False
    db.delete(review)
    db.commit()
    return True