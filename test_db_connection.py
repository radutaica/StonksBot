from database import Database, Symbol
from datetime import datetime

def test_db_connection():
    try:
        # Initialize database connection
        db = Database()
        print("✅ Successfully connected to database")
        
        # Test symbol operations
        test_symbol = "TEST"
        db.save_symbol(test_symbol, "Test Company")
        print("✅ Successfully saved test symbol")
        
        # Verify we can read it back
        symbol = db.session.query(db.session.query(Symbol).filter(Symbol.symbol == test_symbol).exists()).scalar()
        if symbol:
            print("✅ Successfully retrieved test symbol")
        else:
            print("❌ Failed to retrieve test symbol")
        
        # Clean up test data
        db.session.query(Symbol).filter(Symbol.symbol == test_symbol).delete()
        db.session.commit()
        print("✅ Successfully cleaned up test data")
        
        # Close the connection
        db.close()
        print("✅ Successfully closed database connection")
        
    except Exception as e:
        print(f"❌ Database connection test failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_db_connection() 