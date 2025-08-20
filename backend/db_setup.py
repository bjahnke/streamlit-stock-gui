from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.models import Base
from sqlalchemy.engine import URL, create_engine

engine = create_engine(URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password="password",
    host="localhost",
    port=5432,
    database="asset_analysis"
))

# Create all tables defined in the models
Base.metadata.create_all(engine)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Example usage:
# with SessionLocal() as session:
#     # Perform database operations here
#     pass