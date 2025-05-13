from database import Database, Symbol, TimeInterval
from sqlalchemy import func, and_
from datetime import datetime
from collections import defaultdict

def check_duplicates():
    db = Database()
    try:
        print("\n=== Checking for True Duplicates (identical data) ===\n")
        
        # Track statistics
        total_duplicates = 0
        total_symbols = db.session.query(Symbol).count()
        
        # Check for true duplicates (all fields identical)
        for symbol in db.session.query(Symbol).all():
            true_duplicates = db.session.query(
                TimeInterval.symbol_id,
                TimeInterval.start_time,
                TimeInterval.end_time,
                TimeInterval.open,
                TimeInterval.high,
                TimeInterval.low,
                TimeInterval.close,
                TimeInterval.volume,
                TimeInterval.interval_type,
                func.count(TimeInterval.id)
            ).filter(
                TimeInterval.symbol_id == symbol.id
            ).group_by(
                TimeInterval.symbol_id,
                TimeInterval.start_time,
                TimeInterval.end_time,
                TimeInterval.open,
                TimeInterval.high,
                TimeInterval.low,
                TimeInterval.close,
                TimeInterval.volume,
                TimeInterval.interval_type
            ).having(
                func.count(TimeInterval.id) > 1
            ).all()
            
            if true_duplicates:
                print(f"\nFound duplicates for {symbol.symbol}:")
                for (symbol_id, start_time, end_time, open_price, high, low, close, volume, interval_type, count) in true_duplicates:
                    print(f"Time: {start_time} to {end_time}")
                    print(f"Interval Type: {interval_type}")
                    print(f"OHLCV: {open_price:.2f} | {high:.2f} | {low:.2f} | {close:.2f} | {volume}")
                    print(f"Count: {count}")
                    print("---")
                total_duplicates += len(true_duplicates)
            else:
                print(f"No duplicates found for {symbol.symbol}")
        
        # Print summary
        total_intervals = db.session.query(TimeInterval).count()
        
        print(f"\n=== Database Summary ===")
        print(f"Total unique symbols in database: {total_symbols}")
        print(f"Total time intervals: {total_intervals}")
        print(f"Total duplicate entries found: {total_duplicates}")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_duplicates() 