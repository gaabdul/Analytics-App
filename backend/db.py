from sqlalchemy import create_engine, Column, String, Date, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date

# Create SQLite engine
engine = create_engine('sqlite:///analytics.db', echo=True)

# Create declarative base
Base = declarative_base()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class CompanyFact(Base):
    """Company financial facts from Yahoo Finance"""
    __tablename__ = 'company_facts'
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    date = Column(Date, nullable=False)
    fiscal_year = Column(Integer, index=True)  # Added for annual data support
    revenue = Column(Float)
    cost = Column(Float)
    ebitda = Column(Float)
    
    def __repr__(self):
        return f"<CompanyFact(symbol='{self.symbol}', date='{self.date}', fiscal_year={self.fiscal_year}, revenue={self.revenue}, cost={self.cost}, ebitda={self.ebitda})>"

class MacroFact(Base):
    """Macroeconomic facts from FRED"""
    __tablename__ = 'macro_facts'
    
    id = Column(Integer, primary_key=True, index=True)
    series_id = Column(String, index=True, nullable=False)
    date = Column(Date, nullable=False)
    value = Column(Float, nullable=False)
    
    def __repr__(self):
        return f"<MacroFact(series_id='{self.series_id}', date='{self.date}', value={self.value})>"

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database
if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully!") 