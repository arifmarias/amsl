from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database configuration
DATABASE_URL = "sqlite:///project_management.db"

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

def get_database():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database and create all tables"""
    try:
        # Import all models to ensure they are registered with Base
        from database.models import (
            User, Company, TaskDescription, Project, ProjectDocument,
            InitialFinancialProjection, FinalFinancialCost, Disbursement,
            ProfitSharingConfig, MoneyReceipt
        )
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Create default admin user if not exists
        db = SessionLocal()
        try:
            existing_user = db.query(User).filter(User.username == "admin").first()
            if not existing_user:
                import bcrypt
                password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
                admin_user = User(
                    username="admin",
                    password_hash=password_hash.decode('utf-8'),
                    role="admin",
                    full_name="System Administrator",
                    email="admin@company.com",
                    is_active=True
                )
                db.add(admin_user)
                db.commit()
                print("✅ Default admin user created (username: admin, password: admin123)")
        finally:
            db.close()
            
        print("✅ Database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        return False

def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            row = result.fetchone()
            if row[0] == 1:
                print("✅ Database connection successful!")
                return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Test the connection when run directly
    test_connection()
    init_database()