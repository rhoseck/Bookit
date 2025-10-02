from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories import user_repo
from app.schemas.user import UserRead, UserCreate
from app.services.auth import create_access_token, create_refresh_token, decode_access_token
from app.services.security import verify_password
from app.core.config import settings  # Add this import to access settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    print(f"\n=== Starting registration for {user.email} ===")
    try:
        db_user = user_repo.get_user_by_email(db, user.email)
        if db_user:
            print(f"User with email {user.email} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        
        print("Creating new user...")
        new_user = user_repo.create_user(db, user)
        print(f"User created with ID: {new_user.id}")
        
        # Double-check the user was persisted
        saved_user = user_repo.get_user_by_id(db, new_user.id)
        if saved_user:
            print(f"Successfully verified user in database: {saved_user.id}")
        else:
            print("WARNING: User not found in database after creation!")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User creation failed"
            )
            
        return new_user
    except Exception as e:
        print(f"Error during registration: {str(e)}")
        raise

@router.post("/login")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = user_repo.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.access_token_expire_minutes * 60,
        secure=True  # for HTTPS
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/refresh")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    payload = decode_access_token(refresh_token)
    if not payload or "sub" not in payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = user_repo.get_user_by_id(db, payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout():
    # Note: JWT logout typically requires blacklisting, which is not implemented here
    # For simplicity, we assume client discards token
    return None