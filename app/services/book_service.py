from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.db.models import Service
from app.schemas.book_service import ServiceCreate, ServiceUpdate
from sqlalchemy import or_
from uuid import UUID
from fastapi import HTTPException, status

def create_service(db: Session, service_in: ServiceCreate) -> Service:
    try:
        service_data = service_in.model_dump()
        new_service = Service(**service_data)
        db.add(new_service)
        db.commit()
        db.refresh(new_service)
        return new_service
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

def get_services(
    db: Session,
    q: str | None = None,
    price_min: float | None = None,
    price_max: float | None = None,
    active: bool | None = None
) -> list[Service]:
    try:
        query = db.query(Service)
        if q:
            query = query.filter(
                or_(
                    Service.name.ilike(f"%{q}%"), 
                    Service.description.ilike(f"%{q}%")
                )
            )
        if price_min is not None:
            query = query.filter(Service.price >= price_min)
        if price_max is not None:
            query = query.filter(Service.price <= price_max)
        if active is not None:
            query = query.filter(Service.is_active == active)
        return query.all()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

def get_service(db: Session, service_id: UUID) -> Service:
    try:
        service = db.query(Service).filter(Service.id == service_id).first()
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found"
            )
        return service
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

def update_service(db: Session, service_id: UUID, service_in: ServiceUpdate) -> Service:
    try:
        service = get_service(db, service_id)
        for field, value in service_in.model_dump(exclude_unset=True).items():
            setattr(service, field, value)
        db.commit()
        db.refresh(service)
        return service
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

def delete_service(db: Session, service_id: UUID) -> bool:
    try:
        service = get_service(db, service_id)
        db.delete(service)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )