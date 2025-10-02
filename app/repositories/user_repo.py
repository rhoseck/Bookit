from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.db import models
from app.db.models import User, UserRole
from uuid import UUID, uuid4
from app.schemas.user import UserCreate
from app.services.security import hash_password
from fastapi import HTTPException, status
from typing import Optional

def create_user(db: Session, user: UserCreate) -> User:
    print(f"\n=== Starting user creation for {user.email} ===")
    
    try:
        # Generate UUID
        user_id = uuid4()
        print(f"Generated UUID: {user_id}")
        
        # Hash password
        hashed_password = hash_password(user.password)
        print("Password hashed successfully")
        
        # Create user instance
        db_user = models.User(
            id=user_id,
            name=user.name,
            email=user.email,
            hashed_password=hashed_password,
            role=UserRole.USER
        )
        print(f"Created user object with ID: {db_user.id}")
        
        # Add to session and commit
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        print(f"=== User creation successful for {user.email} ===\n")
        return db_user
        
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database error during user creation: {str(e)}")
        if "unique constraint" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        print(f"Unexpected error during user creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email address."""
    try:
        return db.query(User).filter(User.email == email).first()
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database error while fetching user by email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    """Get a user by ID."""
    try:
        return db.query(User).filter(User.id == user_id).first()
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database error while fetching user by ID: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )