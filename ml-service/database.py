"""
Database configuration and models using SQLAlchemy ORM
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
# Default to SQLite (no installation required)
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'sqlite:///./finance_tracker.db'
)

# Create engine
# For SQLite, add check_same_thread=False to allow multi-threading
if DATABASE_URL.startswith('sqlite'):
    engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class Transaction(Base):
    """Transaction model for storing cleaned transactions"""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String(100), index=True, nullable=False)
    description = Column(Text, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(10), nullable=True)  # 'credit' or 'debit'
    category = Column(String(50), nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, description='{self.description[:30]}', amount={self.amount}, type={self.transaction_type})>"


class UploadedFile(Base):
    """Model for tracking uploaded files"""
    __tablename__ = 'uploaded_files'
    
    id = Column(String(100), primary_key=True)
    filename = Column(String(255), nullable=False)
    file_format = Column(String(10), nullable=False)
    file_size = Column(Integer, nullable=False)
    original_rows = Column(Integer, nullable=False)
    cleaned_rows = Column(Integer, nullable=False)
    removed_rows = Column(Integer, nullable=False)
    retention_rate = Column(Float, nullable=False)
    quality_score = Column(Float, nullable=True)
    processing_time = Column(Float, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<UploadedFile(id='{self.id}', filename='{self.filename}')>"


class FinancialSummary(Base):
    """Model for storing financial summaries"""
    __tablename__ = 'financial_summaries'
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String(100), index=True, nullable=False)
    income = Column(Float, nullable=False)
    expense = Column(Float, nullable=False)
    remaining_balance = Column(Float, nullable=False)
    transaction_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<FinancialSummary(file_id='{self.file_id}', income={self.income}, expense={self.expense})>"


class CategoryBreakdown(Base):
    """Model for storing category-wise breakdown"""
    __tablename__ = 'category_breakdowns'
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String(100), index=True, nullable=False)
    category = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<CategoryBreakdown(file_id='{self.file_id}', category='{self.category}', amount={self.amount})>"


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    # Test database connection and create tables
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
