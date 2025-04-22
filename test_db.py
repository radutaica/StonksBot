from database import Database
import yfinance as yf
from datetime import datetime, timedelta

def test_database_connection():
    try:
        # Initialize database
        db = Database()
        print("Successfully connected to the database!")
        
        # Test data collection
        symbol = 'AAPL'
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Get some sample data
        stock = yf.Ticker(symbol)
        data = stock.history(start=start_date, end=end_date)
        
        # Save to database
        db.save_stock_data(symbol, data)
        print(f"Successfully saved data for {symbol}")
        
        # Retrieve data
        saved_data = db.get_stock_data(symbol, start_date, end_date)
        print(f"Retrieved {len(saved_data)} records from database")
        
        db.close()
        print("Database connection closed successfully")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_database_connection() 