from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User, UserRole
from app.services.security import hash_password
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)

def create_default_admin():
    """Create a default admin user if none exists."""
    db = next(get_db())
    try:
        # Check if any admin user exists
        admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()
        
        if not admin_user:
            # Create default admin
            admin_id = uuid4()
            hashed_password = hash_password("admin123456")  # Default password
            
            default_admin = User(
                id=admin_id,
                name="Admin User",
                email="admin@bookit.com",
                hashed_password=hashed_password,
                role=UserRole.ADMIN
            )
            
            db.add(default_admin)
            db.commit()
            db.refresh(default_admin)
            
            logger.info("✅ Default admin user created:")
            logger.info(f"   Email: admin@bookit.com")
            logger.info(f"   Password: admin123456")
            logger.info(f"   ID: {admin_id}")
            
        else:
            logger.info("ℹ️ Admin user already exists, skipping creation")
            
    except Exception as e:
        logger.error(f"❌ Error creating default admin: {str(e)}")
        db.rollback()
    finally:
        db.close()