from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.auth import get_current_user
from app.services.security import hash_password
from app.schemas.user import UserRead, UserUpdate
from app.db.models import User
from app.repositories import user_repo

router = APIRouter(tags=["users"])

@router.get("/me", response_model=UserRead)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user

@router.patch("/me", response_model=UserRead)
def update_my_profile(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user profile."""
    user = user_repo.get_user_by_id(db, current_user.id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user_in.email and user_in.email != current_user.email:
        existing_user = user_repo.get_user_by_email(db, user_in.email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
    
    for field, value in user_in.dict(exclude_unset=True).items():
        if field == "password":
            value = hash_password(value)
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user