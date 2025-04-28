from database import Database, Symbol, TimeInterval
from datetime import datetime, timedelta

def check_database():
    db = Database()
    
    # Check symbols
    print("\n=== Symbols in Database ===")
    symbols = db.session.query(Symbol).all()
    for symbol in symbols:
        print(f"\nSymbol: {symbol.symbol}")
        print(f"Company Name: {symbol.company_name}")
        print(f"Active: {symbol.is_active}")
        print(f"Created: {symbol.created_at}")
        print(f"Last Updated: {symbol.updated_at}")
        
        # Get latest 5 intervals for this symbol
        latest_intervals = db.get_latest_intervals(symbol.symbol, limit=5)
        print("\nLatest 5 intervals:")
        for interval in latest_intervals:
            print(f"Time: {interval.start_time} - {interval.end_time}")
            print(f"OHLC: {interval.open:.2f} | {interval.high:.2f} | {interval.low:.2f} | {interval.close:.2f}")
            print(f"Volume: {interval.volume}")
            print("---")
    
    # Get total counts
    total_symbols = db.session.query(Symbol).count()
    total_intervals = db.session.query(TimeInterval).count()
    
    print(f"\n=== Database Summary ===")
    print(f"Total Symbols: {total_symbols}")
    print(f"Total Time Intervals: {total_intervals}")
    
    db.close()

if __name__ == "__main__":
    check_database() 