from database import Base, Database
from db_config import DATABASE_URL
from sqlalchemy import create_engine

def recreate_database():
    print("Recreating database...")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Drop all tables
    print("Dropping existing tables...")
    Base.metadata.drop_all(engine)
    
    # Create new tables
    print("Creating new tables...")
    Base.metadata.create_all(engine)
    
    print("Database recreation complete!")

if __name__ == "__main__":
    recreate_database() 